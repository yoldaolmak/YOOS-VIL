# YOOS-VIL Development Status

## Current Goal
Fix import paths and runtime integrity after restructuring repo into product surface (`src/`) and ops scripts (`ops/`).

## Files Physically Changed (This Session)
1. **`src/core/database.py`** - Added `VisualMemoryConfig` and `VisualMemoryComponent` classes for backward compatibility
2. **`src/main.py`** - Fixed imports: changed `from src.core.selection` to `from src.core.database` for VisualMemory classes
3. **`src/core/metadata_generator.py`** - Restored from git history, fixed import: `src.core.settings` → `src.utils.config`
4. **`src/utils/config.py`** - Already existed, provides `load_project_env()` and config helpers

## Completed and Verified
- ✅ `src/main.py` compiles without errors
- ✅ `src/core/database.py` compiles and exports required classes
- ✅ `src/core/metadata_generator.py` restored and imports work
- ✅ `from src.main import YOOrchestrator` succeeds
- ✅ All core modules pass `python -m py_compile`
- ✅ Import path structure validated: `src/core/`, `src/services/`, `src/utils/`

## Planned but Not Done
- SQL injection audit (all queries must use parameterized statements)
- Structured logging implementation (JSON format)
- Error handling + retry policy decorators
- Test coverage increase (current ~6%, target 60%+)
- Remove unused deleted module references from imports

## Moved to Ops
Already moved in previous sessions:
- `ops/run_deposit.py` - One-time deposit asset download
- `ops/vision_budget.py` - Budget tracking script
- `ops/repair_*.py` - Repair scripts
- `ops/index_*.py` - Indexing scripts
- `ops/download_licensed_deposit_assets.py` - Licensed asset downloader
- `ops/extract_apple_photos_ml.py` - Apple Photos ML extraction

## Remaining Risks
1. **Deleted modules still imported**: Several deleted files (`yo_cloud_vision.py`, `yo_face_detector.py`, etc.) may still be referenced somewhere
2. **SQL Injection**: LIKE queries in `main.py` and `selection.py` use string formatting instead of parameters
3. **Missing error handling**: No global exception handler or retry logic
4. **No structured logging**: Print statements used instead of proper logging
5. **Test coverage**: Only basic import tests exist

## Last Commands/Tests Run
```bash
python -c "from src.main import YOOrchestrator; print('Main import OK')"
python -m py_compile src/main.py src/core/database.py src/core/metadata_generator.py src/utils/config.py
```

## Open Decisions
1. Should we restore any of the deleted `yo_*.py` modules or refactor their functionality into existing modules?
2. Where should `cloud_vision` functionality live if it's needed by `main.py`?
3. Should `ops/` scripts be kept in the same repo or moved to a separate maintenance repo?

---
Last updated: $(date -u +"%Y-%m-%d %H:%M UTC")
