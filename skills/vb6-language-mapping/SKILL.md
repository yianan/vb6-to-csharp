---
name: vb6-language-mapping
description: Side-by-side VB6 ↔ C# syntax and semantic differences. Auto-load when reading any .frm/.bas/.cls file or translating VB6 statements to C#. Covers declarations, scoping, string concat, default properties, accessor keywords, value vs reference semantics.
---

# VB6 ↔ C# language mapping

Use this when translating VB6 source. **Don't blindly transliterate** — VB6 has implicit semantics (default properties, lenient `Variant` coercions, on-error fallthrough) that have no C# equivalent and would translate to bug-for-bug ports if you tried.

## Declarations

| VB6 | C# | Notes |
|---|---|---|
| `Dim x As Integer` | `int x` (or `short x`, see below) | VB6 `Integer` is 16-bit; almost always safe to widen to `int` |
| `Dim x As Long` | `int x` | VB6 `Long` is 32-bit |
| `Dim x As LongPtr` | `nint x` (or `long`) | platform-pointer-sized |
| `Dim x As Double` | `double x` | |
| `Dim x As Single` | `float x` | |
| `Dim x As Currency` | `decimal x` | **Don't use `double` for money.** |
| `Dim x As String` | `string x` | |
| `Dim x As String * 10` | `string x` (validate length) | fixed-length string; in C# just enforce at write time |
| `Dim x As Date` | `DateTime x` | VB6 `Date` is OLE Automation date (a `Double`). Convert via `DateTime.FromOADate` if migrating raw values. |
| `Dim x As Boolean` | `bool x` | VB6 `True` is `-1`, but `True`/`False` translate fine |
| `Dim x As Variant` | infer the real type or use `object` | see `vb6-data-types` skill — Variants need triage |
| `Dim x As Object` | `object x` | usually a COM interface; in C# use the actual type |
| `Const PI = 3.14` | `const double Pi = 3.14;` | |
| `Public x As Integer` | `public int X { get; set; }` | (in a class) |
| `Private x As Integer` | `private int _x;` | |
| `Friend x As Integer` | `internal int X { get; set; }` | |

## Access modifiers

| VB6 | C# |
|---|---|
| `Public Function F()` | `public T F()` |
| `Private Function F()` | `private T F()` |
| `Friend Function F()` | `internal T F()` |
| `Public Sub S()` | `public void S()` |

`Sub` returns nothing; `Function` returns. The return value is assigned by writing to the function name: `F = 42` ↔ `return 42;` in C#.

## Strings

- **Concat operator**: VB6 `&` (proper) and `+` (works for strings, weird with `Variant`). Always translate to C# `+` or string interpolation.
- **`Chr(13) & Chr(10)`** ↔ `"\r\n"` or `Environment.NewLine`.
- **`vbCrLf`, `vbTab`, `vbNullString`** ↔ `"\r\n"`, `"\t"`, `null` (not `""` — VB6 `vbNullString` is genuinely null).
- **`StrComp(a, b, vbBinaryCompare)`** ↔ `string.Compare(a, b, StringComparison.Ordinal)`. `vbTextCompare` ↔ `StringComparison.OrdinalIgnoreCase` (or current culture if you really want locale-sensitive).

## Default properties (the biggest footgun)

VB6 controls have a **default property**, accessed when you write the control's name without a property:

```vb
Text1 = "hello"        ' actually Text1.Text = "hello"
If Text1 = "" Then     ' actually If Text1.Text = ""
```

When translating, **always** add the explicit property — the C# equivalent has no default property:

```csharp
text1.Text = "hello";
if (string.IsNullOrEmpty(text1.Text)) { ... }
```

Same trap with `Set Foo = New Bar` ↔ just `Foo = new Bar()` in C#. VB6 needed `Set` for object refs vs `Let` (assignment) for values; C# unifies them.

## Loops and control flow

| VB6 | C# |
|---|---|
| `If x Then ... End If` | `if (x) { ... }` |
| `If x Then ... Else ... End If` | `if (x) { ... } else { ... }` |
| `Select Case x` … `Case 1`, `Case 2 To 5`, `Case Else` | `switch (x)` with `case 1:`, range needs `case >= 2 and <= 5:`, `default:` |
| `For i = 0 To n - 1` | `for (int i = 0; i < n; i++)` |
| `For i = 0 To n` | `for (int i = 0; i <= n; i++)` — note inclusive! |
| `For Each x In coll` | `foreach (var x in coll)` |
| `Do While x: ... Loop` | `while (x) { ... }` |
| `Do: ... Loop Until x` | `do { ... } while (!x);` |
| `Exit For`, `Exit Do`, `Exit Sub` | `break`, `break`, `return` |
| `GoTo label` | avoid; usually refactor to early return or restructure |

`On Error Goto` is not control flow — it's exception handling. See the `vb6-error-handling` skill.

## Operators

- **Logical**: VB6 `And`/`Or`/`Not` are bitwise on integers, short-circuit on booleans (mostly). C# has separate `&&`/`||`/`!` (short-circuit) and `&`/`|`/`~` (bitwise).
- **Equality**: VB6 `=` for both assignment and comparison. C# uses `=` for assignment, `==` for comparison.
- **Integer division**: VB6 `\` ↔ C# `/` on integers (or `Math.DivRem`). `Mod` ↔ `%`.

## Object lifetime

VB6 has reference counting (COM-style). `Set foo = Nothing` releases. C# has GC; nulling out a local is rarely needed. For `IDisposable` objects, use `using` blocks instead.

```vb
Set rs = New ADODB.Recordset
rs.Open ...
' ... use rs ...
rs.Close
Set rs = Nothing
```
↔
```csharp
using var connection = new SqliteConnection(connStr);
// using ensures Dispose() — but in EF Core you usually just inject DbContext.
```

## Modules vs classes

A `.bas` module's procedures are global. The closest C# equivalent is a `static class`. But if the module holds shared state (like `library.bas`'s `Public con As New ADODB.Connection`), translate it to a service registered with DI — never to a `static` field. Globals + multi-threading = pain.

## Examples from the seed library app

```vb
' From library.bas
Public con As New ADODB.Connection
Public rs As New ADODB.Recordset
Public Function connect()
    con.Open "Provider=SQLOLEDB.1;..."
End Function
```

Translates to (conceptually):

```csharp
// In Program.cs:
builder.Services.AddDbContext<LibraryDbContext>(opt => opt.UseSqlite(connStr));

// Per-request:
public class SomeEndpoint(LibraryDbContext db) { ... }
```

The global `con`/`rs` become a scoped `DbContext` injected per HTTP request — no global state, no leaking connections.
