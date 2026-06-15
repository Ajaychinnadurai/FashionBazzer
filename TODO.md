# TODO - FashionBazzer (frontend + backend fixes)

## Phase 1: Seed + Dashboard stabilization
- [x] Remove/gate demo/fallback commission generation in `backend/apps/tracker/analytics.py`.
- [x] Harden `frontend/src/components/Dashboard/Dashboard.jsx` against missing/changed API response shapes.
- [x] Add frontend seed trigger calling `GET /api/dashboard/seed/`.


## Phase 2: Validate
- [x] Run `frontend` build.

- [ ] Run `backend` tests.
- [ ] Smoke test dashboard endpoints.
