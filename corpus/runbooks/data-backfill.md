# Data backfill runbook

Backfills run from the warehouse replica. Dry-run against the staging database,
compare row counts, then schedule the production run overnight.
