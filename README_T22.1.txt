Astro-Zodiac T22.1 — Supabase Migration

Purpose:
Restore the actual PostgreSQL schema and prepare it for Supabase DEV.

Next:
1. Copy `supabase/` into the repo.
2. Commit the migration files.
3. Link the local repo to Astro-Zodiac-DEV.
4. Run `supabase db push`.
5. Verify the tables in Supabase Studio.

This package does not migrate customer data.
