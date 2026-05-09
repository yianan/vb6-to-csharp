---
description: Restore and migrate data from a SQL Server .bak into the migrated SQLite database.
argument-hint: <path-to-backup.bak> [optional notes]
---

Use this command only when the user has chosen to migrate existing data rather than start from a fresh seed.

Load the `mssql-bak-to-sqlite` skill, then:

1. Confirm the `.bak` path from `$ARGUMENTS` exists.
2. Restore the backup in a local SQL Server Docker container.
3. Inspect tables and row counts before exporting anything.
4. Export source tables to CSV or use a scripted reader when CSV quoting would be unsafe.
5. Compare the source schema with the migrated EF Core schema.
6. Write an import script that performs any required denormalized-to-normalized transformations.
7. Import into a fresh SQLite database created by EF Core migrations.
8. Verify row counts and run the app's smoke script.

Do not silently drop unresolved rows. Log them, summarize them to the user, and ask for a decision if the mapping is ambiguous.

If Docker is unavailable or the backup restore fails because of unknown SQL Server logical file names, stop and show the exact restore diagnostic. Do not guess `MOVE` names; run `RESTORE FILELISTONLY` first.
