# Deploy runbook

1. Freeze the release branch.
2. Run the smoke suite against the staging database.
3. Promote the build.

Production deploys stop at 15:00 on Fridays.
Rollbacks are covered in the rollback runbook.
