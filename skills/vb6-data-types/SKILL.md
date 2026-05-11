---
name: vb6-data-types
description: Map VB6 data types (Variant, Currency, Date, fixed-length strings) and array semantics (1-based, Option Base, Redim) to C#. Auto-load when reading any code containing Variant, Currency, ReDim, Option Base, or array indexing.
---

# VB6 data types → C#

The previous skill (`vb6-language-mapping`) has the simple primitive map. This one covers the messy ones.

## `Variant` — triage required

`Variant` holds anything: a number, a string, a date, an object, an empty value, or `Null`. VB6 coerces between them implicitly. C# has no exact equivalent — the closest is `object`, but you almost always know the actual type from context.

**Translation strategy**:

1. **Read the surrounding code** to identify what the `Variant` is actually used as.
2. Pick the concrete C# type.
3. Replace operations that depended on coercion with explicit conversions.

| VB6 pattern | What it actually is | C# |
|---|---|---|
| `Dim x As Variant: x = TextBox1.Text` | always a string | `string x = textBox1.Text` |
| `Dim x As Variant: x = 0` then `x = "n/a"` | sentinel — sometimes a number, sometimes string | refactor; usually `int?` + a separate flag, or a discriminated union |
| `If IsNull(x) Then` | x came from a recordset field | `if (reader["Foo"] is DBNull)` or use EF Core's nullable types directly (`int?`, `string?`) |
| `If IsEmpty(x) Then` | x is `Variant` and never assigned | doesn't happen in C#; remove the check |
| `If IsNumeric(x) Then` | x is a string-ish thing | `int.TryParse(x, out var n)` |
| `Variant` array (e.g. `rs.GetRows`) | rectangular `object[,]` | translate to a `List<T>` of typed records (LINQ projection) |

## `Currency` — use `decimal`, never `double`

VB6 `Currency` is a 64-bit fixed-point type, scale 4 (e.g. `1.2345`). It exists to avoid floating-point rounding for money.

Translate to `decimal` in C#. **Never `double` for money** — it has the same rounding problems VB6's `Currency` was designed to avoid.

EF Core SQLite stores `decimal` as TEXT; configure precision in the DbContext:

```csharp
b.Entity<Book>().Property(x => x.Cost).HasPrecision(10, 2);
b.Entity<Fine>().Property(x => x.Amount).HasPrecision(10, 2);
```

## `Date` — use `DateTime`, sometimes `DateOnly`

VB6 `Date` is an OLE Automation date — a `Double` where the integer part is days since 1899-12-30 and the fractional part is the time. It always carries a time, even if you only use the date.

- Translate to `DateTime` in most cases.
- If the field is genuinely date-only (issue date, due date), prefer `DateOnly` (.NET 6+) — but EF Core SQLite handles it via a converter; simplest is to keep `DateTime` and zero out the time at write.
- VB6's `Now` ↔ `DateTime.UtcNow` (prefer UTC; convert to local at the UI layer).
- VB6's `DateDiff("d", a, b)` ↔ `(b - a).TotalDays` (cast to `int` to truncate, or `Math.Floor` to floor-truncate).

```vb
' VB6
fine = DateDiff("d", issue_date, Now) * 0.5
```
↔
```csharp
var days = (int)Math.Floor((DateTime.UtcNow - issueDate).TotalDays);
var fine = days * 0.5m;  // decimal, not double
```

## Fixed-length strings (`String * 10`)

```vb
Dim code As String * 10
```

VB6 pads/truncates to exactly 10 chars. In C# just use `string` and validate at write:

```csharp
if (code.Length != 10) throw new ArgumentException("Code must be exactly 10 chars");
```

Or for a column, set `[MaxLength(10)]`/`HasMaxLength(10)` and let EF Core enforce it.

## Arrays

VB6 arrays are **1-based by default** in many idiomatic patterns, but it depends on `Option Base`:

```vb
Option Base 1   ' arrays start at 1
Dim arr(10) As Integer   ' valid indices: 1..10  (10 elements)
```

Without `Option Base 1`, arrays start at 0:

```vb
Dim arr(10) As Integer   ' valid indices: 0..10  (11 elements!)
```

**Critical**: `Dim arr(10)` reserves indices 0 through 10 inclusive — that's 11 slots, not 10. C# `new int[10]` is 10 slots, indices 0..9.

When translating loops, watch for `For i = 1 To UBound(arr)` patterns. Translate to:

```csharp
for (int i = 0; i < arr.Length; i++) { ... }
// NOT: for (int i = 1; i <= arr.Length; i++)  -- off by one
```

`UBound(arr)` ↔ `arr.Length - 1` (NOT `arr.Length`).
`LBound(arr)` ↔ `0` (assuming you've moved to 0-based).

## `ReDim` and `ReDim Preserve`

```vb
ReDim arr(20)             ' resize, lose contents
ReDim Preserve arr(20)    ' resize, keep contents
```

Translate to a `List<T>` (preferred) — no resize ceremony. If you need a fixed-size array specifically:

```csharp
var arr = new int[21];                    // ReDim arr(20) with 1-based — 21 slots
Array.Resize(ref arr, 21);                // ReDim Preserve, keeps contents
```

But genuinely, `List<T>` is the right answer 95% of the time.

## Examples from the seed library app

The original library app uses `Variant` very lightly (mostly through `rs.Fields("col_name").Value`), no `Option Base`, and stored money in a column whose declared type isn't visible (it's a SQL Server `money`). In the rewrite:

- `Cost`, `Amount`, and `RatePerDay` are all `decimal` with `HasPrecision(10, 2)`.
- `IssueDate`/`DueDate`/`ReturnDate` are `DateTime` (UTC); we display as local date in the React UI via `toLocaleDateString()`.
- The 15-day loan period is added with `DateTime.UtcNow.AddDays(15)`, not `DateAdd`.
- Fine days are calculated with `(int)Math.Floor((asOf.Date - dueDate.Date).TotalDays)`.

## Stringly-typed numerics (anti-pattern)

In the seed library app, `book1.copies` and `book1.cost` are stored as **strings** in SQL Server but used arithmetically — `new_cpy = cpy - 1` works because VB's Variant coerces strings to numbers transparently. This produces several bugs:
- `'9' < '10'` is *false* lexically — sort order is broken.
- Concatenating with `&` looks the same as adding with `+`; one operator change silently corrupts data.
- A `NULL` from the DB becomes `""` which becomes `0` in arithmetic but `""` in concat — non-uniform behavior.

When translating, pick the right primitive type at the schema boundary even if the original was string:
- **Counts** → `int` with a `>= 0` check.
- **Money** → `int CostCents` (preferred for SQLite) or `decimal Cost` with `HasPrecision`.

Don't be tempted to keep the column as `TEXT` "for compatibility" — there's no consumer of the legacy schema in the new app.
