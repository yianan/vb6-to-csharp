---
name: vb6-ado-patterns
description: Translate VB6 ADO patterns (global ADODB.Connection/Recordset, inline SQL with string concat, manual MoveNext loops) to ASP.NET Core + EF Core (DI'd DbContext, parameterized LINQ, transactions). Auto-load when reading any code with ADODB.Connection, Recordset, .Open "select", rs.MoveNext, or rs.Fields(...).
---

# VB6 ADO → ASP.NET Core + EF Core

The most common VB6 data-access pattern is:

1. A `.bas` module declares `Public con As New ADODB.Connection` and `Public rs As New ADODB.Recordset` as globals.
2. Forms call a `connect()` function that opens `con` to the database.
3. Each form builds a SQL string by concatenating user input from textboxes and calls `rs.Open SQL, con`.
4. Results are read via `rs.Fields("col_name").Value` and a `Do While Not rs.EOF / rs.MoveNext / Loop` cursor.

Every step of this is wrong by 2026 standards. The translation isn't a port — it's a redesign.

## The pattern, translated

| VB6 | C# / EF Core |
|---|---|
| Global `ADODB.Connection` | `LibraryDbContext` registered with `AddDbContext<>` (scoped per HTTP request) |
| Global `ADODB.Recordset` | gone; LINQ queries return concrete `List<T>` or stream `IAsyncEnumerable<T>` |
| Inline SQL via string concat | LINQ (`db.Books.Where(b => b.Title.Contains(q))`) — always parameterized |
| `rs.Open "select … where id = " & id, con` | `await db.Books.FindAsync(id)` |
| `rs.MoveNext` cursor | `await foreach (var b in db.Books.AsAsyncEnumerable())` or `.ToListAsync()` |
| `rs.Fields("col").Value` | strongly-typed property: `book.Title` |
| `con.Execute "insert into … values('" & x & "')"` | `db.Books.Add(b); await db.SaveChangesAsync();` |
| Manual transactions (none in most VB6 code) | `await using var tx = await db.Database.BeginTransactionAsync(); ... await tx.CommitAsync();` |

## SQL injection — the universal smell

Every VB6 form in any old codebase will have queries like:

```vb
rs.Open "select * from login where user_name = '" & TextBox1.Text & "' and password = '" & TextBox2.Text & "'", con
```

This is a textbook SQL injection. The translation is **not** "carefully escape the strings" — it's "use parameterized queries":

```csharp
var user = await db.Users.FirstOrDefaultAsync(u => u.Username == username);
if (user is null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash)) return Unauthorized();
```

LINQ to EF Core always parameterizes. If you need raw SQL for some reason, use `FromSqlInterpolated`:

```csharp
var books = await db.Books.FromSqlInterpolated($"select * from Books where Title = {q}").ToListAsync();
//                                                                                    ^^^^ becomes a parameter, not interpolated
```

**Never** use `FromSqlRaw` with concatenated strings. If you find yourself building a SQL string at runtime, you've taken a wrong turn — use LINQ.

## Multi-statement business logic

The VB6 issue-book flow is typically:

```vb
con.Execute "update book1 set copies = copies - 1 where id = " & bookId
con.Execute "insert into student_book (...) values (...)"
```

Two separate statements, no transaction. If the second fails, the first is committed and your data is wrong.

Translate to a service method:

```csharp
public async Task<(Loan? loan, string? error)> IssueAsync(int memberId, int bookId, CancellationToken ct = default)
{
    await using var tx = await db.Database.BeginTransactionAsync(ct);

    var book = await db.Books.FindAsync([bookId], ct);
    if (book is null) return (null, "Book not found");
    if (book.AvailableCopies <= 0) return (null, "No copies available");

    book.AvailableCopies -= 1;
    var loan = new Loan { MemberId = memberId, BookId = bookId, IssueDate = DateTime.UtcNow, DueDate = DateTime.UtcNow.AddDays(15) };
    db.Loans.Add(loan);
    await db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
    return (loan, null);
}
```

The transaction guarantees both writes commit or neither does. The result tuple distinguishes "expected failure" (member doesn't exist, no copies) from "unexpected failure" (DB connection lost — that throws).

## Schema modernization

VB6 schemas are typically denormalized — instead of FKs, the dependent table copies the parent's columns. The seed library app's `student_book` table embeds member name/address and book ISBN/subject, so issuing a book "froze" a snapshot.

In the rewrite, **don't replicate this**. Use FKs:

```csharp
public class Loan
{
    public int Id { get; set; }
    public int MemberId { get; set; }
    public Member Member { get; set; } = null!;
    public int BookId { get; set; }
    public Book Book { get; set; } = null!;
    public DateTime IssueDate { get; set; }
    public DateTime DueDate { get; set; }
    public DateTime? ReturnDate { get; set; }
}
```

If the original truly needed an audit snapshot (rare — usually it was just easier to write that way in VB6), add an `audit_log` table or an `is_archived` history scheme. Don't carry forward the denormalization.

## DAO and Access sources

Some VB6 apps use DAO or ship Access files instead of SQL Server backups. Inventory these separately from ADO code:

| VB6 / Access | C# / EF Core |
|---|---|
| `Database` | `DbContext` |
| `TableDef` / `CreateField` | entity configuration and EF migration |
| `Recordset` | `DbSet<T>` query result or tracked entity |
| `QueryDef` with parameters | LINQ with variables or `FromSqlInterpolated` |
| `Recordset.AddNew` / `.Edit` / `.Update` | tracked entity insert/update plus `SaveChangesAsync` |
| `Recordset.Delete` | `Remove` plus `SaveChangesAsync` |
| `MoveLast` solely for `RecordCount` | `CountAsync` |
| `rs.Filter = "..."` | composed LINQ predicates or parameterized SQL |

For `.mdb` files in WSL2, `mdbtools` can often inspect and export:

```sh
sudo apt-get update
sudo apt-get install -y mdbtools
mdb-tables source.mdb
mdb-schema source.mdb sqlite
mdb-export source.mdb TableName
```

For `.accdb`, support varies. If `mdbtools` cannot read the file, record a Windows export follow-up using Access, ODBC, PowerShell, or a small Windows/.NET export utility.

Rules:

- Preserve table and column names initially with EF table/column mapping, then rename behind DTOs if useful.
- Convert DAO table/schema creation code into migrations before porting UI.
- Do not use Access OLEDB/ACE providers in WSL2 runtime code.
- If the source creates an Access database at startup and no real data file is supplied, seed only source-defined rows and mark real data import as blocked until an export is available.

## Common gotchas

- **Recordset cursors are stateful**. `rs.MoveFirst` / `rs.MoveNext` / `rs.MoveLast` patterns turn into a single `.ToListAsync()` plus normal indexing. If you find code that mutates `rs` and reads it later in the same procedure, treat the result list as immutable and rebuild as needed.
- **Recordset `.Filter` and `.Sort`** are in-memory operations on the same recordset; in EF Core you re-query with the new `Where`/`OrderBy`.
- **CursorType / LockType / CursorLocation** parameters on `rs.Open` are mostly irrelevant — EF Core handles change tracking and concurrency for you. If the VB6 code used `adLockOptimistic` or `adLockPessimistic`, that's a hint about concurrency expectations; consider EF Core's `[ConcurrencyCheck]` attribute on hot fields like `Book.AvailableCopies`.
- **`rs.Fields(0)`** (positional) means whatever the SQL `SELECT` listed first. After translating to LINQ + a strong type, that becomes a named property. If the original code is dependent on positions, double-check the column order in the SQL.
- **Column names can lie.** In the seed library app, `student_book.issue_date` actually stores the *due date* (issued + 15 days); the true issue date is `date1`. Don't trust column names — always cross-reference with what `rs.Fields(n)` is read into in the UI, or with `DateAdd`/`DateDiff` math nearby. When in doubt, rename to something unambiguous (`IssuedAt`/`DueAt`) in the new schema rather than preserve the misleading name.
- **`rs.Open SQL, ...` against INSERT/UPDATE/DELETE statements** — ADO tolerates this and discards the (empty) recordset, but the right modern idiom is `db.SaveChangesAsync()` after mutating tracked entities; never open a recordset against a mutation.

## Cycle-handling for entity serialization

When endpoints return EF entities directly with bidirectional navigations (e.g. `Member.Loans` ⇄ `Loan.Member`), the JSON serializer hits an infinite cycle. Configure once:

```csharp
builder.Services.Configure<JsonOptions>(o =>
{
    o.SerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
    o.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});
```

This is fine for v1. The proper fix later is to project to DTOs in the endpoint:

```csharp
g.MapGet("/loans", async (LibraryDbContext db) =>
    await db.Loans.Select(l => new LoanDto(l.Id, l.Book.Title, l.Member.Name, l.IssueDate, l.DueDate, l.ReturnDate)).ToListAsync());
```
