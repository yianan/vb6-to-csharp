---
name: vb6-error-handling
description: Translate VB6 error handling (On Error Goto, On Error Resume Next, Err.Number/Description) to C# try/catch. Auto-load when reading any .frm/.bas with these constructs. Distinguishes legitimate error handling from fatalistic anti-patterns that should not be ported.
---

# VB6 error handling → C# `try`/`catch`

VB6's error model is goto-based and procedure-scoped. C#'s is exception-based and scoped to `try` blocks. They map cleanly **when the VB6 code is actually handling errors**. They emphatically don't map when the VB6 code is just suppressing them — and you'll see plenty of that.

## The four common VB6 patterns

### 1. `On Error Goto label` — handle and continue

```vb
Public Sub SaveBook()
    On Error Goto handler
    rs.Open "insert into book1 ...", con
    Exit Sub
handler:
    MsgBox "Error: " & Err.Description
End Sub
```

Translate to a normal `try`/`catch`:

```csharp
public async Task SaveBookAsync(Book b)
{
    try
    {
        db.Books.Add(b);
        await db.SaveChangesAsync();
    }
    catch (Exception ex)
    {
        // surface to UI through the API response, not MsgBox
        throw new ApplicationException($"Failed to save book: {ex.Message}", ex);
    }
}
```

Notes:
- `MsgBox` doesn't translate — in a web app, errors return as HTTP 4xx/5xx with a message. The frontend shows them.
- `Err.Number` ↔ catch the specific exception type or inspect inner exceptions.
- `Err.Description` ↔ `ex.Message`.
- `Err.Source` ↔ `ex.Source` (rarely useful).

### 2. `On Error Resume Next` — suppress and continue (DON'T PORT VERBATIM)

```vb
On Error Resume Next
SomethingThatMightFail
SomethingElse
```

This is almost always a bug or laziness — it silently swallows every error in the procedure. Don't translate to a giant empty `catch`. **Read the code first** to understand what error the original author was trying to ignore (often: "object doesn't exist yet, OK to skip"), then write narrow logic for that case:

```csharp
// Original intent: clear text fields if a control happens to be missing
// (it never is, but VB6 was paranoid)
text1?.Text = "";  // null-conditional; no try/catch needed

// Or: the original was suppressing a specific error that's not a real error in C#
// (e.g. file already exists)
if (!File.Exists(path)) File.Create(path).Dispose();
```

If you genuinely can't figure out what the original was trying to do, leave a `// TODO(vb6 port): On Error Resume Next was here, behavior unclear` comment and **don't** wrap things in `try { } catch { }`. A silent catch is worse than a crash because it hides the real problem.

### 3. `On Error Goto 0` — disable handler, let it propagate

```vb
On Error Goto 0
```

This restores default error behavior (crash). In C# this is just… the default. Delete the line.

### 4. `Err.Raise N, source, description` — raise an error

```vb
Err.Raise 9, "MyForm", "Index out of bounds"
```

Translate to throwing a real exception:

```csharp
throw new IndexOutOfRangeException("Index out of bounds");
```

Pick the closest BCL exception type. Don't introduce custom exception types unless callers need to distinguish them.

## Anti-patterns to fix during the port

| VB6 anti-pattern | What to do |
|---|---|
| Empty `On Error Resume Next` at top of every procedure | Delete; rely on caller to handle. Add narrow checks where actually needed (null guards, `TryParse`, `File.Exists`). |
| `MsgBox Err.Description` and exit | Throw the exception; let the API layer convert it to a response. UI handles display. |
| Errors used as control flow ("try to open the recordset, if it fails treat as no rows") | Use a `null`-safe lookup: `await db.X.FirstOrDefaultAsync()` returns `null`, no exception. |
| Catching every error and continuing in a transaction | Hard fail. Wrap the whole logical operation in a transaction with `using var tx = ...; await tx.CommitAsync();` and let the failure roll back. |
| `On Error Goto handler` followed by silent log + return | Keep the catch but log via `ILogger` and rethrow or return a typed error result; don't swallow. |
| **`MsgBox vbYesNo` confirmation with the branches inverted** (Yes runs the destructive op; No falsely reports success) | Single Cancel/Confirm modal; Confirm performs the action; Cancel does nothing and shows no message. **Do not faithfully port** the lying-Else branch — it's a bug, not behavior. Seen in the seed library app's `Book_Details.frm:537-550` and `member_details.frm` delete confirmations. |

## When the original code didn't handle errors at all

A lot of VB6 forms just don't have error handlers — the runtime kills the whole app on any error. In C# / ASP.NET Core, unhandled exceptions in an endpoint become a 500. That's usually fine for v1; ASP.NET Core's developer exception page will show the stack trace.

For production, add a global exception handler middleware that logs and returns a sanitized 500 — but don't paper over real bugs in the meantime.

## Examples from the seed library app

The original library app had **zero error handlers** in the forms. Every form's `_Click` handler just hits the database and trusts it works. The migrated version benefits from this:

- Endpoints throw on bad input (`Results.BadRequest`).
- `LoanService.IssueAsync` returns `(Loan?, string?)` — successful tuple has loan, failed has reason. Never throws for "expected" failures (member doesn't exist, no copies available); throws only for unexpected ones (DB connection lost). The endpoint maps the reason to a 400.
- The frontend's `ApiError` class surfaces the message in the UI.

This is closer to a Result type than to traditional exceptions, and it works because the failure modes are well-bounded.
