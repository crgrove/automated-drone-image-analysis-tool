# Batch Processing — Feature Status

**Branch:** `feature/batch-processing`
**Status:** Implemented and verified; not yet committed.
**Last updated:** 2026-05-21

## Goal

ADIAT analyses routinely involve 2,000+ images. The established workflow is to
split imagery into folders of ~150 images and analyze each separately so that a
failure in one folder does not lose the rest. This feature builds that workflow
into ADIAT: point it at a parent folder and it analyzes **each subfolder as its
own batch**, one at a time, isolating per-folder failures.

## Decisions

| Question | Decision |
|----------|----------|
| Entry point | Both a built-in UI checkbox **and** a headless CLI; the CLI can set algorithm settings. |
| Batch unit | Each subfolder that directly contains images = one batch. No auto-chunking. |
| Coordinator | Auto-create an `ADIAT_Search_*.xml` Search Coordinator project linking every successful batch, while each batch's `ADIAT_Data.xml` stays standalone-openable. |

## Components

### 1. `BatchAnalyzeService` (engine)
`app/core/services/BatchAnalyzeService.py` — `QObject` orchestrator.

- `discover_batch_folders()` — walks the input parent, returns every folder
  directly containing an image. Skips the output tree and any
  `ADIAT_Results` / `.thumbnails` folders so generated results are never
  re-ingested as input.
- `process_batches()` (`@Slot`) — runs each folder through a standard
  `AnalyzeService` pass sequentially; a per-folder exception is caught and
  recorded so remaining folders still run.
- `_batch_output_dir()` — mirrors each batch's path under the output root.
- `_create_search_project()` — builds the `ADIAT_Search_*.xml` via
  `SearchProjectService`.
- `_write_summary()` — writes `batch_summary.txt` to the output root.
- Signals: `sig_msg(str)`, `sig_batch_progress(int, int, str)`,
  `sig_done(int, int, str)`.

### 2. MainWindow UI
`app/core/controllers/images/MainWindow.py` — adds a "Batch mode" checkbox to
the directories layout. When checked, Start runs `BatchAnalyzeService` on a
`QThread`; progress streams to the log; completion offers an "Open Search
Coordinator" button. State persists via `settings_service` key `BatchMode`.

### 3. Headless CLI
`app/core/services/cli/BatchCLI.py`, invoked as `python app batch ...`.

- Required: `--input`, `--output`.
- Algorithm settings via `--config <xml>` (reuses an existing `ADIAT_Data.xml`'s
  settings), individual flags (`--algorithm`, `--min-area`, etc.), and
  repeatable `--option NAME=VALUE`. Resolution order: defaults → `--config` →
  flags → `--option`.
- `--no-coordinator`, `--project-name`, `--coordinator-name` control the
  Search Coordinator project.

### Supporting change
`AnalyzeService.__init__` gained a `recursive=True` flag. Batch mode passes
`recursive=False` so each `AnalyzeService` pass is scoped to a single folder
instead of walking the whole tree.

## Files

**Modified:** `app/__main__.py`, `app/core/controllers/images/MainWindow.py`,
`app/core/services/AnalyzeService.py`,
`app/tests/core/services/test_analyze_service.py`

**Added:** `app/core/services/BatchAnalyzeService.py`,
`app/core/services/cli/` (`__init__.py`, `BatchCLI.py`),
`app/tests/core/services/test_batch_analyze_service.py`,
`app/tests/core/services/cli/` (`__init__.py`, `test_batch_cli.py`)

## Output layout

The output root should be **separate from the input parent folder** — never the
input folder itself or an ancestor of it (discovery would prune everything and
find zero batches). Generated results are skipped on re-runs, and
`AnalyzeService` only ever deletes its own `ADIAT_Results` subfolder, so source
imagery is never at risk.

Batch output folder names **mirror the input folder names** — the algorithm name
is not appended. The recommended pattern is one output root per algorithm run:

```
D:\Survey2026\
  Imagery\            <- input parent (Batch1, Batch2, ...)
  Results_AI\         <- output root for the AI run
    Batch1\ADIAT_Results\ADIAT_Data.xml
    Batch2\ADIAT_Results\ADIAT_Data.xml
    ADIAT_Search_Imagery_<timestamp>.xml
    batch_summary.txt
  Results_MRMAP\      <- output root for a separate MRMAP run
```

## Verification

- 36 new tests pass (`test_batch_analyze_service.py`, `test_batch_cli.py`,
  two new `test_analyze_service.py` cases) plus dependency-service tests.
- CLI smoke test: 3 folders processed end-to-end produced 3 `ADIAT_Data.xml`
  files, the linking `ADIAT_Search_*.xml`, and `batch_summary.txt`, exit code 0.
- Two pre-existing `MainWindow` test failures were confirmed NOT regressions —
  they fail identically on clean `master` (missing test data fixture).

## Open items

- **Per-folder algorithm tag (proposed, not built):** output folders currently
  mirror input names (`Batch1` → `Batch1`). An optional `--tag` / UI field could
  append the algorithm tag so `Batch1` → `Batch1_AI`, matching the existing
  manual naming convention. Awaiting decision.
- Not yet committed.
