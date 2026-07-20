# CLAUDE.md — ADIAT Engineering Standards

This file is auto-loaded as project context. It defines normative engineering standards for AI-assisted development in this repository. `MUST` means required, `SHOULD` means preferred unless there is a documented reason not to.

## 1. Repository Baseline

- **Application:** Automated Drone Image Analysis Tool (ADIAT), desktop GUI for drone image analysis (SAR-focused).
- **Language/runtime:** Python 3 + PySide6 (Qt 6).
- **Entry point:** [app/__main__.py](app/__main__.py) (`main()`), launching `SelectionDialog` and then Images (`MainWindow`) or Streaming (`StreamViewerWindow`).
- **Algorithm registry:** [app/algorithms.conf](app/algorithms.conf) (JSON).
- **Packaging and build:**
  - UI/resources compile: `python setup.py build_res`
  - App package build: `python setup.py bdist_app` (PyInstaller-backed)
- **Lint config:** [.flake8](.flake8) (`max-line-length = 160`, `extend-ignore = F401, E402`).
- **Test framework:** `pytest` + `pytest-qt` (`qt_api=pyside6` in [pytest.ini](pytest.ini)).

## 2. Core Development Standards

### 2.1 Layering and Responsibilities

- **Controllers** (`*/controllers/*.py`) MUST contain UI orchestration only:
  - signal/slot wiring
  - view state updates
  - validation and service delegation
- **Services** (`*/services/*.py`) MUST contain business logic and I/O orchestration.
- **Helpers** ([app/helpers/](app/helpers/)) MUST remain cross-cutting utilities; do not place feature workflows here.
- **Views:**
  - generated files (`*_ui.py`, `*_rc.py`) MUST be treated as generated artifacts
  - custom behavior MUST live in non-generated view/controller files

### 2.2 Plugin and Algorithm Contracts

- Image algorithms under `app/algorithms/images/<AlgorithmName>/` MUST include:
  - `controllers/`
  - `services/`
  - `views/`
  - package `__init__.py`
- Image algorithm controllers MUST implement `get_options()`, `validate()`, and `load_options()` from `AlgorithmController`.
- Image algorithm services MUST implement `process_image()` from `AlgorithmService`.
- New **image** algorithms MUST be registered in [app/algorithms.conf](app/algorithms.conf) under `"algorithms"` with complete metadata:
  - `name`, `label`, `controller`, `wizard_controller`, `service`, `type`, `platforms`
  - `combine_overlapping_aois` SHOULD be set explicitly.
- Algorithm names in config MUST match implementation naming consistently (no typos or alias drift).

### 2.2.1 Streaming Architectural Consistency

- New **streaming** algorithms MUST be registered in [app/algorithms.conf](app/algorithms.conf) under `"streaming_algorithms"` with metadata:
  - `name`, `label`, `controller`, `module` (dotted path to the controller module), `platforms`
  - Streaming entries deliberately omit `wizard_controller`, `service`, and `type` — the controller resolves its own services via `get_stream_service()` (see below).
- Streaming algorithms MUST follow a normalized processing contract:
  - `StreamAlgorithmService` ([app/core/services/streaming/StreamAlgorithmService.py](app/core/services/streaming/StreamAlgorithmService.py))
  - `StreamProcessResult` + `StreamDetection` ([app/core/services/streaming/contracts.py](app/core/services/streaming/contracts.py))
- Streaming frame orchestration in worker paths MUST go through `StreamAnalyzeService` ([app/core/services/streaming/StreamAnalyzeService.py](app/core/services/streaming/StreamAnalyzeService.py)).
- `StreamViewerWindow` MUST NOT contain algorithm-specific detection conversion branches.
  - New/updated algorithms MUST plug into the shared contract rather than adding `hasattr(...)` dispatch branches.
- Streaming controllers MUST expose `get_stream_service()` returning the worker-thread service object.
- Streaming services/adapters MUST implement lifecycle hooks:
  - `reset()`
  - `cleanup()`
- Legacy streaming services that do not natively match the contract MUST use adapters in:
  - [app/core/services/streaming/adapters.py](app/core/services/streaming/adapters.py)
- AI tools MUST avoid introducing circular imports between:
  - `core.services.streaming.*`
  - `algorithms.streaming.*`
  - especially via package-level `__init__.py` side effects.

### 2.3 Configuration and Extensibility

- Algorithm selection MUST be config-driven from [app/algorithms.conf](app/algorithms.conf).
- AI changes SHOULD avoid hardcoded algorithm routing tables in orchestration code.
- If hardcoded dispatch is unavoidable, the same change MUST include:
  - explicit rationale in code comments
  - tests proving unknown/unsupported services fail clearly

### 2.4 Logging, Error Handling, and Diagnostics

- Production-path code MUST use `LoggerService` (or Python logging through it) for diagnostics.
- New production-path `print()` calls MUST NOT be introduced.
- Exceptions in long-running workflows MUST include context (which file/algorithm/operation failed).

### 2.5 Data Compatibility and Persistence

- Changes to persisted artifacts MUST preserve read-compatibility:
  - `ADIAT_Data.xml`
  - algorithm options dictionaries
  - pickle-backed data (`drones.pkl`, `xmp.pkl`, `colors.pkl`)
- If schema/shape changes are necessary, code MUST support old and new formats during a transition period.
- Backward-compatibility behavior MUST be tested.

### 2.6 UI and Generated Files

- Developers/AI MUST NOT manually edit generated `*_ui.py` and `*_rc.py` files.
- UI source-of-truth is `.ui` / `.qrc`; regenerate with `python setup.py build_res`.
- Production UI surfaces (dialogs, pages, algorithm widgets, wizard widgets) MUST be backed by `.ui` files under [resources/views/](resources/views/).
- Corresponding generated Python UI modules (`*_ui.py`) MUST be regenerated and committed with `.ui` changes.
- Controllers/widgets SHOULD use generated `Ui_*` classes for production UIs rather than building equivalent layouts purely in code, unless there is a documented exception.
- Build environments used for UI regeneration MUST have `pyside6-uic` and `pyside6-rcc` available.

### 2.7 Naming and File Hygiene

- File/module names MUST be intentional and correctly spelled.
- Package markers MUST use `__init__.py` (not near-miss names).
- Public-facing algorithm identifiers MUST be stable and typo-free.

### 2.8 Translation Integration (i18n)

- All user-facing text in algorithm controllers/views (`app/algorithms/**/controllers/*.py`, `app/algorithms/**/views/*.py`) MUST be translation-ready:
  - use `self.tr("...")` in Python-created widgets and runtime labels/tooltips/messages
  - keep `.ui` text in [resources/views/](resources/views/) so generated `*_ui.py` uses `QCoreApplication.translate(...)`
- UI logic MUST NOT depend on translated display text:
  - combo boxes and selectors MUST use stable internal values via `itemData`/enums/ids
  - persistence/service configs MUST read and write stable keys, not localized labels
- Manually maintained UI modules (non-generated `*_ui.py`) MUST implement `retranslateUi(...)` and set visible strings there.
- Translation extraction/compilation MUST be run when text changes:
  - `python scripts/extract_translations.py`
  - `python scripts/extract_translations.py --compile` (or equivalent release build path)

### 2.9 Mandatory New Functionality Requirements

- All new functionality MUST include automated test coverage.
  - At minimum, add/update targeted tests proving the new behavior and critical error paths.
- All new functionality MUST include a `flake8` scan before finalization.
  - Minimum acceptable scope: changed files.
  - Preferred scope: `flake8 app/`.
- All new user-facing functionality MUST include translation support.
  - Visible strings MUST use translation-ready patterns from Section 2.8.
  - Translation extraction/compilation MUST be run when text changes.

## 3. Testing Standards

### 3.1 Test Placement

- All tests live under [app/tests/](app/tests/).
- Location by domain:
  - algorithms: `app/tests/algorithms/images/...`
  - core services: `app/tests/core/services/...`
  - core controllers: `app/tests/core/controllers/...`
  - core views/widgets/dialogs: `app/tests/core/views/...`
  - streaming: `app/tests/streaming/unit/...` and `app/tests/streaming/integration/...`
  - helpers: `app/tests/helpers/...`

### 3.2 Required Test Updates by Change Type

- Algorithm service changes MUST update/add service tests in `app/tests/algorithms/images/<AlgorithmName>/test_*_service.py`.
- Algorithm controller/wizard changes MUST update/add tests in `app/tests/algorithms/images/<AlgorithmName>/test_*.py` and/or relevant core controller tests.
- Core service changes MUST update/add tests in matching `app/tests/core/services/...`.
- UI/controller behavior changes MUST include pytest-qt coverage (`qtbot`) for interaction flows.
- Config/persistence format changes MUST include regression tests for old and new formats.
- Streaming contract/orchestration changes MUST include:
  - unit tests for adapters/contracts/orchestrator behavior
  - integration tests for `StreamViewerWindow` processing path
  - verification that worker-thread processing still emits normalized detections.

### 3.3 Test Style and Determinism

- New tests SHOULD be pytest function-style for simple cases; class-based grouping is allowed for larger suites.
- Use fixtures from [app/tests/conftest.py](app/tests/conftest.py) where appropriate:
  - `testData`
  - `app`
  - `main_window`
  - `thermal_sdk_available`
- New tests MUST be deterministic:
  - no external network dependency unless explicitly integration-scoped and guarded
  - no reliance on execution order
- Temporary files/directories MUST use `tempfile` fixtures/helpers.

## 4. Quality Gates for AI Changes

After each meaningful code change, AI MUST run relevant checks (targeted first, full suites when practical):

1. **Lint:**
   - `flake8 app/` (preferred) or changed-file scope (minimum)
2. **Targeted tests:**
   - `pytest app/tests/path/to/affected_test.py`
3. **Domain-level regression** (as needed):
   - `pytest app/tests/core/services`
   - `pytest app/tests/algorithms/images`
   - `pytest app/tests/streaming/unit`

If a full run is too expensive, AI MUST state exactly what was run and what was not run.

## 5. AI Change Workflow (Definition of Done)

Before finalizing a change, AI MUST verify and report:

1. Correct layer placement (controller vs service vs helper vs view).
2. No manual edits to generated UI/resource Python files.
3. Backward compatibility impact and mitigation.
4. Tests added/updated in the correct `app/tests/...` location for new functionality.
5. `flake8` scope executed and outcome.
6. Translation support added/verified for new user-facing text, including extraction/compile steps when text changed.
7. Lint/test commands executed and their outcome.
8. Any unresolved risks or deferred follow-ups.

## 6. Scope Discipline

- This guide is implementation policy, not a historical status report.
- Avoid embedding volatile repository statistics (for example, counts of tests/files) or dated audit snapshots.
- Prefer durable, normative requirements describing what changes MUST/SHOULD do.
