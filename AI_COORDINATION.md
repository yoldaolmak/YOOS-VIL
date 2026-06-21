# YOOS-VIL Coordination Contract

This file is the canonical instruction set for ongoing YOOS-VIL product work.

## Product Goal

YOOS-VIL must be a reusable application surface, not a collection of one-off scripts.

It must support two simultaneous workflows:

1. Operator workflow:
   When Kemal says "attach images to post `POST_ID` with VIL", the protocol must run reliably end to end.
2. Reusable product workflow:
   Another site/profile must be able to use the same engine through the same core surface.

## Non-Negotiable Rules

1. Do not optimize repo appearance by breaking runtime behavior.
2. Do not delete a file if any runtime path still imports or calls it.
3. Do not report planned architecture as completed architecture.
4. Unpushed work is not done.
5. Every completed milestone must be committed and pushed.
6. Update `QWEN_STATUS.md` after each milestone with:
   - what is physically done
   - what is still planned
   - what was tested
   - what failed

## Canonical Product Shape

The system is split into three layers.

### 1. Product Core

Path: `src/vil/`

This layer contains reusable business logic only.

Target modules:

- `src/vil/engine/selector.py`
- `src/vil/engine/processor.py`
- `src/vil/engine/publisher.py`
- `src/vil/engine/metadata.py`
- `src/vil/engine/quality.py`
- `src/vil/engine/gallery.py`
- `src/vil/providers/wordpress.py`
- `src/vil/profiles/yoldaolmak.py`
- `src/vil/config.py`

Responsibilities:

- select candidate images for a post
- apply image processing and filtering
- generate metadata
- upload media to WordPress
- build native gallery/image blocks
- enforce site-specific rules through profiles

### 2. App Surface

Path: `src/vil/app/`

Target modules:

- `src/vil/app/cli.py`
- `src/vil/app/api.py`
- `src/vil/app/jobs.py`
- `src/vil/app/health.py`
- `src/vil/app/server.py`
- `src/vil/app/state.py`

Responsibilities:

- CLI entrypoint
- HTTP surface
- background job orchestration
- structured health checks
- job state tracking

### 3. Ops

Path: `ops/`

Only one-off or maintenance scripts belong here:

- repair scripts
- migration scripts
- indexing helpers
- diagnostics
- backfills

These are not the product surface.

## Canonical User Contract

The first stable public contracts are CLI and HTTP.

CLI shape:

```bash
vil attach --site yoldaolmak --post 264459
vil attach --site yoldaolmak --post 264459 --count 4 --lang tr --people-first
vil review --site yoldaolmak --post 264459
vil plan --site yoldaolmak --post 264459 --count 4 --people-first
vil process --site yoldaolmak --post 264459 --count 4 --people-first
vil health
vil serve --host 127.0.0.1 --port 8040
```

HTTP shape:

- `GET /health`
- `POST /review`
- `POST /plan`
- `POST /process`
- `POST /attach`
- `POST /jobs/attach`
- `GET /jobs`
- `GET /jobs/{job_id}`

## Required Structured Output

The attach pipeline should return machine-readable output with fields like:

- `site`
- `post_id`
- `selected_assets`
- `rejected_assets`
- `uploaded_media_ids`
- `inserted_blocks`
- `warnings`
- `duration_ms`

Job endpoints should additionally expose:

- `job_id`
- `status`
- `created_at`
- `updated_at`
- `payload`
- `result`
- `error`

## Current State

The branch has already completed the earlier stabilization work.

Current verified surface:

- canonical `src/vil/*` package root exists
- CLI exists and is tested
- native `plan`, `process`, and `attach` contracts exist
- minimal HTTP surface exists and is tested
- async attach job registry exists and is tested

Still incomplete:

- auth on HTTP surface
- persisted job store
- richer native metadata parity with legacy path
- gradual retirement of legacy internals in `src/main.py` and `src/core/*`

## Immediate Implementation Order

### Milestone A: Secure the HTTP Surface

Tasks:

1. Add token-based auth for HTTP endpoints.
2. Keep health behavior explicit and intentional.
3. Ensure error payloads stay structured.

### Milestone B: Persist Job State

Tasks:

1. Replace in-memory-only registry with persistent storage.
2. Preserve job history across restarts.
3. Keep the HTTP contract stable.

### Milestone C: Reduce Legacy Dependency

Tasks:

1. Move more attach behavior from legacy orchestrator paths into `src/vil/engine/*`.
2. Keep backward compatibility only where necessary.
3. Remove dead code only after callers are updated.

## Do Not Do

- Do not invent a second parallel architecture.
- Do not hide runtime breakage behind README claims.
- Do not delete domain-specific runtime modules just because they look messy.
- Do not merge work that is untested in the current environment.

## Required Working Style

After every meaningful step:

1. update `QWEN_STATUS.md`
2. commit
3. push

If a step is only partially complete, say so clearly.
