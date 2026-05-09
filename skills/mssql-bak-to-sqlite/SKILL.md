---
name: mssql-bak-to-sqlite
description: Restore a SQL Server .bak file in Docker, export tables to CSV, import into a fresh SQLite DB built from EF Core migrations. Auto-load when a VB6 project ships a .bak file and the user opted into data migration. NOT yet exercised end-to-end against the seed library app — pattern documented but the script needs hardening.
---

# SQL Server `.bak` → SQLite

This skill is **partial**. The pattern is documented; the script has not been run end-to-end against a real `.bak`. Use it as a starting point, expect to debug.

## When this is needed

The user opted into "migrate existing data" during the architecture interview. The source app shipped a `.bak` file (typically in `database/`).

If the user picked "fresh seed", skip this entirely — the migration plan should generate seed data instead.

## Strategy

1. **Restore** the `.bak` in a SQL Server Docker container (no need to install SQL Server natively, especially on macOS/Linux).
2. **Inspect** the live schema and data — confirm it matches the inventory.
3. **Export** each table to CSV.
4. **Map types** SQL Server → SQLite (most map cleanly; `money`, `datetime2`, `bit` need attention).
5. **Import** the CSVs into the SQLite DB the EF Core migrations created. Use a Python or C# script if the schema diverges (denormalized → normalized) so you can do per-row transforms.

## Restore in Docker

```sh
docker run --rm -d --name liba-mssql \
  -e ACCEPT_EULA=Y \
  -e MSSQL_SA_PASSWORD='YourStrong!Passw0rd' \
  -p 1433:1433 \
  -v "$PWD/database":/backups \
  mcr.microsoft.com/mssql/server:2022-latest

# Wait ~10 seconds for SQL Server to start
sleep 10

# Restore
docker exec liba-mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P 'YourStrong!Passw0rd' \
  -Q "RESTORE DATABASE liba FROM DISK = '/backups/liba.bak' \
      WITH MOVE 'liba' TO '/var/opt/mssql/data/liba.mdf', \
           MOVE 'liba_log' TO '/var/opt/mssql/data/liba_log.ldf'"
```

If the logical file names aren't `liba` and `liba_log`, list them first:

```sh
docker exec liba-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P '…' \
  -Q "RESTORE FILELISTONLY FROM DISK = '/backups/liba.bak'"
```

The `LogicalName` column has the values to use in `MOVE` clauses.

## Inspect the schema

```sh
docker exec liba-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P '…' -d liba \
  -Q "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'"

docker exec liba-mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P '…' -d liba \
  -Q "SELECT TOP 5 * FROM book1"
```

## Export tables

`bcp` is the fastest path:

```sh
docker exec liba-mssql /opt/mssql-tools/bin/bcp \
  liba.dbo.book1 out /backups/book1.csv \
  -S localhost -U sa -P '…' -c -t','
```

Or via SQL with `sqlcmd -o output.csv -s "," -W` for smaller tables. Doublecheck that fields containing commas or newlines are quoted — `bcp` does not quote by default. For dirty data, write a Python script with `pyodbc` instead.

## Type mapping

| SQL Server | SQLite (via EF Core) | Notes |
|---|---|---|
| `int`, `bigint`, `smallint`, `tinyint` | `INTEGER` | direct |
| `bit` | `INTEGER` | 0/1 |
| `varchar(n)`, `nvarchar(n)`, `text`, `ntext` | `TEXT` | direct |
| `char(n)`, `nchar(n)` | `TEXT` (trim trailing whitespace) | SQL Server pads CHAR to n, SQLite doesn't |
| `datetime`, `datetime2`, `smalldatetime` | `TEXT` (ISO-8601) | EF Core handles via converter |
| `date` | `TEXT` (`YYYY-MM-DD`) | |
| `money`, `smallmoney`, `decimal(p,s)` | `TEXT` (decimal) | configure `HasPrecision(p, s)` in DbContext |
| `uniqueidentifier` | `TEXT` (GUID string) | |
| `varbinary(max)`, `image` | `BLOB` | rare; usually small icons in `.frx` files instead |

## Import into SQLite

If the rewrite's schema is normalized (the usual case — see `vb6-ado-patterns`), you can't bulk-import the CSV directly. Write a small Python script:

```python
import csv, sqlite3
con = sqlite3.connect("backend/Library.Api/library.db")
con.execute("PRAGMA foreign_keys = ON")

# Members: original `member1` → new `Members`
with open("database/csv/member1.csv") as f:
    for row in csv.reader(f):
        member_id, name, local_addr, perm_addr, phone, mtype, gender = row
        con.execute(
            "INSERT INTO Members (Id, Name, LocalAddress, PermanentAddress, Phone, Type, Gender, IsArchived, CreatedAt) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))",
            (int(member_id), name, local_addr, perm_addr, phone, mtype, gender),
        )
con.commit()

# Books, Loans, Fines: similar; for `student_book` (denormalized), look up MemberId/BookId by name/ISBN
# For records that can't be resolved, log them and leave as-is (don't drop silently).
```

Notes:
- **Reset the SQLite DB** before importing: `rm library.db; dotnet-ef database update`. EF runs the migration cleanly; then your script populates it.
- **Disable identity-insert checks** by writing the original `Id` directly when possible; otherwise let SQLite assign new ones and remap.
- **Date conversion**: SQL Server `bcp` exports dates as `YYYY-MM-DD HH:MM:SS.SSS`. SQLite accepts this directly via the EF Core `DateTime` converter.
- **Money**: emerges as a string with optional currency symbol; strip and parse.

## Cleanup

```sh
docker stop liba-mssql
```

(`--rm` removes the container; the data is gone with it. Re-run the restore to start fresh.)

## What this skill is missing

- Validated end-to-end script for the seed library app (`liba.bak`).
- Handling for tables with binary columns, computed columns, or triggers.
- Ratchet for incremental re-imports (re-running the script should be idempotent).
- A test harness that spins up a SQL Server container, restores a fixture `.bak`, and verifies the resulting SQLite matches expected counts.

If you do exercise this against a real `.bak`, please update this skill with what you learned.
