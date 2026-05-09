---
name: vb6-frm-parser
description: Reference for the VB6 .frm file format — structure of control declarations, attribute lines, the Attribute VB_Name boundary that separates layout from code. Auto-load when reading .frm files for inventory or translation.
---

# `.frm` file format

A VB6 form file is two halves glued together:

1. **Top half**: layout — control tree as a nested `Begin <ControlType> <Name> … End` block.
2. **Bottom half**: code — the form module, separated from the layout by `Attribute VB_Name = "FormName"`.

Both halves are plain text but the layout half uses VB6's own form-serialization grammar.

## Top of the file

```
VERSION 5.00
Object = "{5E9E78A0-531B-11CF-91F6-C2863C385E30}#1.0#0"; "MSFLXGRD.OCX"
Object = "{67397AA1-7FB1-11D0-B148-00A0C922E820}#6.0#0"; "MSADODC.OCX"
Begin VB.Form FormName
   Caption         =   "Form Title"
   ClientHeight    =   3000
   ClientWidth     =   4500
   …
   Begin VB.TextBox Text1
      Height          =   285
      Left            =   120
      Text            =   "default"
      Top             =   240
      Width           =   1215
   End
   Begin VB.CommandButton Command1
      Caption         =   "OK"
      Default         =   -1  'True
      Height          =   375
      Left            =   1440
      TabIndex        =   1
      Top             =   240
      Width           =   855
   End
End
Attribute VB_Name = "FormName"
Attribute VB_GlobalNameSpace = False
…
```

## Parsing the layout half

For an inventory pass, you don't need a full parser — a line-oriented scanner is enough:

- `Object = "{guid}#…"; "FILE.OCX"` — external control library (record for the inventory's external dependencies).
- `Begin <Class> <Name>` — start of a control. `<Class>` is the type (`VB.TextBox`, `VB.CommandButton`, `VB.MDIForm`, `VB.Form`, or library-specific like `MSFlexGridLib.MSFlexGrid`, `MSDataGridLib.DataGrid`, `MSAdodcLib.Adodc`).
- `End` — close the most recent `Begin`. Tracks via a stack; `Begin`/`End` can nest (containers like `Frame`, `MDIForm`).
- Attribute lines `Property = Value` — extract `Caption`, `Text`, `DataField`, `RecordSource`, `Style`, `MultiLine`, `PasswordChar`, etc. for the controls you care about.

A 100-line regex script gets you 95% of the way. For the rare control with weird syntax (e.g. multi-line property values quoted with `:`), fall back to manual reading.

## Common control classes you'll see

| Class | What it is |
|---|---|
| `VB.Form`, `VB.MDIForm`, `VB.MDIChild` | top-level forms |
| `VB.Frame` | grouping container; contains other controls |
| `VB.PictureBox` | image or drawable surface; may contain controls |
| `VB.TextBox`, `VB.Label` | text fields and labels |
| `VB.CommandButton`, `VB.OptionButton`, `VB.CheckBox` | buttons and toggles |
| `VB.ComboBox`, `VB.ListBox` | choice lists |
| `VB.Image` | static image (`PictureBox` is the heavyweight one) |
| `VB.Timer` | invisible control; fires events |
| `VB.Menu` | menu items (typically nested inside the form's `Menu` block) |
| `MSFlexGridLib.MSFlexGrid` | a sortable read-only grid (most common in old apps) |
| `MSDataGridLib.DataGrid` | data-bound grid |
| `MSAdodcLib.Adodc` | data control (no UI; just connection + recordset) |
| `MSDBGrid.DBGrid` | older data-bound grid |
| `MSComctlLib.ListView`, `.TreeView`, `.ToolBar` | common-controls pack |
| `RICHTEXT.RichTextCtrl` | rich text |

## Code half

After `Attribute VB_Name = "FormName"` (and a few more `Attribute …` lines), the rest of the file is normal VB6 code:

- Form-level variable declarations (`Private foo As Integer`)
- Event handlers (`Private Sub Command1_Click()` / `Private Sub Form_Load()`)
- Helper procedures
- Inline SQL via `rs.Open "..."` and `con.Execute "..."`
- Calls to module-level procedures (e.g. `connect` from `library.bas`)

Event handler names follow the pattern `<ControlName>_<EventName>` — e.g. `Command1_Click`, `Form_Load`, `Text1_KeyPress(KeyAscii As Integer)`. This is enough to map "what code runs when the user does what" without parsing further.

## Tips

- **`.frx` files** are binary — they hold control resources (icons, embedded images, RichText state). You can't read them as text, but you usually don't need to: control declarations referring to `.frx` data look like `Picture = "FormName.frx":0000`. Just note them in the inventory.
- **`Attribute VB_Name`** appears in `.bas` and `.cls` files too, marking module/class names.
- **Forms with a Menu** have a nested `Begin VB.Menu` tree at the top of the form. Menu item names get `_Click` handlers in code (`mnuFileExit_Click`).
- **Control arrays** look like `Begin VB.TextBox Text1 Index = 0`. Multiple controls share a name; the `Index` distinguishes them. Event handlers receive the index: `Text1_Change(Index As Integer)`. In React, this is just an array of inputs rendered with `.map`.

## Output for an inventory

For each form, the parser should emit:

```json
{
  "name": "Login",
  "caption": "Library Login",
  "controls": [
    { "type": "VB.TextBox", "name": "Text1" },
    { "type": "VB.TextBox", "name": "Text2", "passwordChar": "*" },
    { "type": "VB.CommandButton", "name": "Command1", "caption": "Login" }
  ],
  "events": ["Form_Load", "Command1_Click"],
  "sql_queries": [
    "select * from login where user_name = '<TextBox1.Text>' and password = '<TextBox2.Text>'"
  ],
  "opens_forms": ["MDIlibrary"],
  "external_dependencies": []
}
```

The architect agent reads this; missing a control means missing a feature.
