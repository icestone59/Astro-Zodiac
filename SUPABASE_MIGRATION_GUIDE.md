# Astro-Zodiac — Supabase DEV Migration Guide

## 1. Copy the `supabase/` folder into the repository root.

Result:

```text
supabase/
└── migrations/
    ├── 20260904000000_initial_postgres.sql
    └── 20260904000001_auth_runtime.sql
```

## 2. Link the local repo to Astro-Zodiac-DEV

From the repository root:

```bash
supabase login
supabase link --project-ref <ASTRO_ZODIAC_DEV_PROJECT_REF>
```

## 3. Push versioned migrations

```bash
supabase db push
```

## 4. Verify tables in Supabase Studio

Expected core tables:

```text
users
user_profiles
membership_grants
orders
payments
webhook_events
charts
analyses
validation_sessions
action_plans
daily_checkins
weekly_reviews
plan_adjustments
ai_usage_events
user_sessions
```

## 5. Migration rule

Supabase recommends keeping remote schema changes in versioned migration
files. Avoid making ad-hoc schema changes directly on the remote project once
this migration workflow is adopted.

## 6. Secrets

Never commit:
- DATABASE_URL
- database passwords
- Supabase service-role keys
- access tokens
