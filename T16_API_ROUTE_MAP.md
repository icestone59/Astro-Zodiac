# T16 API Route Map

T16 provides framework-neutral application use-cases. HTTP adapters stay thin.

| Method | Route | Use case |
|---|---|---|
| POST | `/api/v1/auth/register` | T13 `register()` |
| POST | `/api/v1/auth/login` | T13 `authenticate()` + session |
| GET | `/api/v1/me` | T16 `current_user()` |
| POST | `/api/v1/analysis/free` | T16 `analyze_free()` |
| POST | `/api/v1/patterns/{pattern_id}/validate` | T16 `validate_candidate()` |
| GET | `/api/v1/patterns/{pattern_id}/psychology` | validated-pattern gate |
| POST | `/api/v1/action-plans` | validated-pattern gate |
| POST | `/api/v1/tracking/start` | T16 `start_tracking()` |
| GET | `/api/v1/entitlements/{feature}` | T16 `check_feature_access()` |
| POST | `/api/v1/payments/webhook` | T14 verified webhook -> T15 integration |

Rules: frontend never grants access; payment webhooks never trust client-side payment state; AI is not invoked on the deterministic Free path.
