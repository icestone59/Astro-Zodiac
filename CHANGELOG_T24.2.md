# CHANGELOG — T24.2

- Fixed PostgreSQL auth adapter to match T13 AuthRepository contract.
- Corrected user primary key column from `id` to `user_id`.
- Corrected session repository contract.
- Added password hash persistence through the canonical auth service.
- Added regression tests for user, password-hash, and session lookup.
