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

**The documented exceptions.** Two categories of widget have no declarative form, and requiring a `.ui` for them would produce a file that describes nothing. A class in either category MUST carry a `# 2.6 exception:` comment naming which, so the exemption is a decision someone made rather than an omission nobody noticed:

1. **Widgets instantiated N times at runtime from a controller** — repeated row and list-item widgets (`ColorRowWidget`, `HSVColorRowWidget`, `MatchedFilterRowWizardWidget`, `RecentColorWidget`, …). Qt Designer has no concept of "build this once per colour the operator adds".
2. **Custom-painted primitives** — classes that implement `paintEvent` and mouse handling instead of composing child widgets (`HueRingSelector`, `RangeSlider`, `Toggle`, `ColorWheelWidget`, `HSVRangePickerWidget`, `ClickableColorSwatch`, `OverlayWidget`, …). Their appearance is code by nature.

Everything else that builds layout in Python is a violation awaiting conversion, not an exception. The dialogs under [app/core/views/images/viewer/dialogs/](app/core/views/images/viewer/dialogs/), the shared tabs under [app/core/views/streaming/components/](app/core/views/streaming/components/), the streaming algorithm control widgets, and `CoordinatorWindow` are the known backlog; convert by operator exposure when touching one for another reason.

**Hand-maintained `*_ui.py`.** A `*_ui.py` with no `.ui` beside it is not a generated file, so the first rule above does not protect it — but it is also not exempt from § 2.8. Until it is converted it MUST implement `retranslateUi` and set its visible strings there, and it MUST spell `QCoreApplication.translate(...)` out at every call site: `pyside6-lupdate` matches that call syntactically, so binding it to a local alias runs correctly and extracts **nothing**, leaving the strings with no catalog entry in any language while the file reads as fully internationalized. `scripts/extract_translations.py` distinguishes the two kinds by the presence of a `.ui`; `app/tests/helpers/test_ui_module_hygiene.py` enforces both rules.

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

### 2.9 Event-Driven Sequencing (No Timers as Coordination)

- Timers MUST NOT be used as a substitute for event/message-driven sequencing.
  - Waiting a fixed delay for another operation to "settle" (an image load, a layout pass, a signal cascade) is prohibited. Code MUST consume a completion signal/event, or use an explicit request/consume handoff where the initiating side states its intent and the completing side applies it (reference pattern: `Viewer.load_image_with_zoom` consumed by `ImageLoadController._apply_pending_view_zoom`).
  - Rationale: a fixed delay encodes an assumption about machine speed. It passes on the development machine and fails in the field (network volumes, slower hardware, macOS timing differences), and each failure invites another, longer timer.
- State that must survive later events MUST be held where those events can respect it (e.g. a held zoom lives in the viewer's `zoomStack`; geometry/visibility handlers re-project it rather than discard it), not re-asserted by deferred checks.
- Timers remain legitimate where the delay itself is the requirement: periodic polling of sources that emit no events, UI timeouts (toasts), and debouncing/batching of high-frequency events.

### 2.10 Mandatory New Functionality Requirements

- All new functionality MUST include automated test coverage.
  - At minimum, add/update targeted tests proving the new behavior and critical error paths.
- All new functionality MUST include a `flake8` scan before finalization.
  - Minimum acceptable scope: changed files.
  - Preferred scope: `flake8 app/`.
- All new user-facing functionality MUST include translation support.
  - Visible strings MUST use translation-ready patterns from Section 2.8.
  - Translation extraction/compilation MUST be run when text changes.

### 2.11 Altitude References

ADIAT carries **three** aircraft altitudes. They are different numbers, they are equal only over flat ground, and confusing them is the highest-value mistake to design against: the error is zero on the bench and grows with terrain relief, so it appears only in the field, over the ground a search team is actually working.

| Reference | Meaning | Label |
|---|---|---|
| **ATO** | height above the **takeoff point** — barometric, DJI's `rel_alt`; does not change when terrain rises | `ATO` |
| **AGL** | height above the **terrain beneath the aircraft** — measured or DEM-derived | `AGL` |
| **MSL** | height above mean sea level | `MSL` |

- ATO and AGL MUST NOT share a field, a column, or a label. "AGL" MUST mean height above terrain everywhere in ADIAT; a takeoff-relative value MUST be called ATO.
- Live telemetry keys (the wire dict *is* the contract — see [TelemetryEnrichmentService.py](app/core/services/telemetry/TelemetryEnrichmentService.py)):

  | Key | Meaning |
  |---|---|
  | `aircraft_altitude_msl_m` | MSL |
  | `aircraft_altitude_agl_m` | **ATO.** Wire name kept for compatibility with recorded bundles and shipped ADIAT Flight builds; it has always carried ATO |
  | `aircraft_altitude_agl_terrain_m` | **AGL**, or absent when none was resolved |
  | `agl_source` | provenance of `aircraft_altitude_agl_terrain_m` only. ADIAT Flight sends this as `aircraft_altitude_agl_source` (`UPPER_SNAKE`, unconditionally, including `TAKEOFF_REFERENCE`); `_stamp_source` folds it into `agl_source` at ingest so there is one provenance name internally and in recorded bundles, and leaves the raw key in place so `telemetry.jsonl` stays faithful to the wire |
  | `terrain_elevation_m` | DEM elevation beneath the aircraft |

- **Provenance MUST be checked before presenting an AGL.** Presence of `aircraft_altitude_agl_terrain_m` — never `agl_source` — decides whether an AGL exists; `publisher_agl_source()` and `has_publisher_agl()` decide whether it was actually referenced to terrain. `takeoff_reference` (Flight looked and found no terrain source) MUST stay distinguishable from an absent source name (a publisher predating the field): both earn a DEM lookup, but only the first can be reported to the operator as such. An AGL that was not MUST be marked (the HUD appends `*`). Unknown source names MUST pass through rather than be dropped.
- `agl_source == "reported"` predates this rule and is kept verbatim for bundle comparability: it means "ATO only, no AGL resolved".
- ADIAT Flight's AGL outranks Desktop's inference; enrichment MUST pass such an envelope through without a DEM lookup. The live differential anchors, best first: the publisher's **takeoff coordinates** (`takeoff_latitude`/`takeoff_longitude` — positions are datum-free, Desktop samples its own DEM at the launch point, and a viewer connecting mid-flight still anchors correctly), then the first fix for publishers predating the fields. Anchor bookkeeping MUST run on every fix so a mid-flight fallback is already armed when the publisher stops resolving AGL.
- `TelemetryEnrichmentService._absolute_agl` (the `MSL − geoid − terrain` path) is **intentionally inert in production**: the DEM worker is built with `enable_geoid=False` because `GeoidService` mutates thread-affine PROJ state and hard-crashed a real session. Do not "fix" it, and do not re-enable the geoid on the telemetry thread to make its tests live.
- **`aircraft_altitude_msl_m` has an undetermined datum, from either source.** Treat it as ellipsoidal-or-unknown and NEVER difference it against a DEM without a geoid correction:
  - DJI SRT `abs_alt` is a GPS height above the WGS84 ellipsoid ([video.csv](app/video.csv): "NB abs_alt is ELLIPSOIDAL, not orthometric").
  - ADIAT Flight's is DJI's own ASL frame (RTK fusion when available, else `KeyAltitude + KeyTakeoffLocationAltitude`), and DJI does not document `KeyTakeoffLocationAltitude`'s datum. Measured against the orthometric Copernicus DEM on the 2026-06-10 Georgetown flights it disagreed by ~26 m — the local geoid separation — so the evidence points to ellipsoidal there too. The `aircraft_altitude_msl_m` KDoc in Flight's `TelemetryPublisher.kt` records this at the point of consumption.
  - The error runs −20 to −30 m across CONUS **in the direction that overstates height above terrain**, which is the one direction an AGL must never err in. `ImageService`/`WaldoMetadataService` reached the same conclusion for EXIF GPS altitude and apply `convert_ellipsoidal_to_orthometric` first.
- **`aircraft_altitude_agl_terrain_m` needs no datum correction at all** — that is the whole reason it exists. Both ADIAT Flight's `TERRAIN_DEM` chain and `TelemetryEnrichmentService._anchored_agl` build it from a *difference* of DEM samples anchored where ATO is zero, so any constant datum offset cancels exactly. Code MUST NOT "improve" either by folding an MSL term in; that is the mistake that overstated height above terrain ~3× on mobile.
- **Image path:** `drone-dji:RelativeAltitude` is ATO for DJI imagery and a genuine terrain-referenced AGL for WALDO-prepassed imagery. The pre-pass marks its own output with `drone-dji:AltitudeType` = `terrain`; `ImageService.get_altitude_reference()` reads it back. That reference is for **labelling and diagnostics only** — no GSD, AOI-geolocation or coverage calculation may branch on it without its own change and its own tests. An absent marker means ATO.
- **The flight altitude anchor** ([AltitudeAnchorService.py](app/core/services/image/AltitudeAnchorService.py)) is the one model for image-path altitude: estimate the takeoff point's elevation, then `camera_elevation = anchor + ATO` per frame (barometric precision) and `AGL = camera_elevation − DEM(point)`. AOI geolocation, GSD, the altitude readout and POD all resolve through it; the viewer registers the mission via `set_mission_images()`.
  - **Anchors are per flight segment, never per mission.** A SAR folder holds several flights by several pilots from several launch sites, so the registry segments automatically — aircraft serial first (simultaneous pilots interleave in capture time), then capture-time gaps (`MISSION_SEGMENT_GAP_S`) — and consumers address anchors by image path. An image that cannot be tied to a flight anchors nothing and falls back; one flight's launch frame MUST never anchor another flight's images.
  - The general registry (`strict_datum`) accepts two kinds of evidence, strongest first: a **near-ground frame** (ATO ≤ 10 m → DEM at that position; the datum never enters), and the **baro datum test**. DJI slaves recorded absolute altitude to the barometer — measured on a real 238-frame mission the implied-constant spread was exactly 0.0 — so `median(GPSAltitude − ATO)` recovers the firmware's takeoff estimate exactly, and the datum question collapses to two candidates separated by the geoid undulation. The candidate sitting on ground the flight overflew wins; both, neither, or an undulation too small to separate refuses, and the fallback stands.
  - The raw GPS ensemble MUST NOT anchor general consumers however coherent it is — a constant datum offset is perfectly coherent. POD alone keeps it, bounded by its sensor max range, with its documented conservative residual bias.
  - There is no operator takeoff-elevation input: tying every image back to a launch point is not something a multi-pilot SAR workflow can do, so a knob demanding it is a trap.
  - Without an anchor every path falls back to the pre-existing cross-checked chains (`_select_effective_agl`); with one, the per-frame cross-check is skipped — real takeoff-to-nadir relief would otherwise be misread as datum error.
  - Per-airframe `GPSAltitude` datums are **unverified** (n=1 evidence suggests at least one DJI writes orthometric; `video.csv` documents SRT `abs_alt` as ellipsoidal; WALDO treats Canon airframe GPS as ellipsoidal deliberately). Never infer a datum from one dataset; the anchor model exists so nobody has to.
- User-facing altitude labels MUST come from `FormatHelper.altitude_reference_abbreviation()` / `altitude_reference_phrase()` so a value's reference plane travels with it. Exports (KML, CalTopo, PDF) spell the plane out; tight UI uses the abbreviation.
- An operator-entered override (`AltitudeController.custom_agl_altitude_ft`, the streaming wizard's altitude) is height above the ground being flown over — label it AGL, not ATO.
- ADIAT Flight and Desktop both label sea level **MSL** as of Flight's ASL→MSL string pass; the wire key was always `aircraft_altitude_msl_m`.

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
