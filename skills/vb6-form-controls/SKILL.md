---
name: vb6-form-controls
description: Map VB6 form controls (TextBox, MSFlexGrid, MSADODC, DataGrid, ComboBox, MDIForm, modal dialogs) to React equivalents. Auto-load when reading any .frm file or translating VB6 form layouts.
---

# VB6 controls → React/HTML

VB6 forms are absolute-positioned with hardcoded pixel coordinates. **Don't transcribe layout** — recreate function in a sensible flexbox/grid layout. This skill is about control *behavior*.

## Per-control translation

| VB6 control | React equivalent | Notes |
|---|---|---|
| `TextBox` | `<input type="text" value=… onChange=…>` | controlled component; use `useState` |
| `TextBox` (`PasswordChar = "*"`) | `<input type="password">` | |
| `TextBox` (`MultiLine = True`) | `<textarea>` | |
| `Label` | `<span>` or `<label>` | use `<label>` if it's the caption for an input |
| `CommandButton` | `<button onClick=…>` | use `type="button"` inside forms to avoid accidental submit, or `type="submit"` for the primary action |
| `ComboBox` (`Style = 0` Dropdown Combo) | `<input list=…>` + `<datalist>` (free-typing) | |
| `ComboBox` (`Style = 2` Dropdown List) | `<select>` | strict choice |
| `CheckBox` | `<input type="checkbox" checked=… onChange=…>` | |
| `OptionButton` (radio) | `<input type="radio" name=… value=…>` | group via `name` |
| `Frame` | `<fieldset>` + `<legend>` | or just a `<section>` with a heading |
| `ListBox` | `<select size={6}>` or a list of clickable rows | for multi-select use `multiple` |
| `MSFlexGrid` (read-only) | `<table>` (or shared `<DataGrid>` component) | |
| `MSFlexGrid` (editable) | a `<table>` with `<input>` per cell | rare; consider whether the data model needs per-row dialogs instead |
| `DataGrid` (`MSDatGrd.ocx`) | shared `<DataGrid>` component | always read-only in our migration; edits go through detail dialogs |
| `MSADODC` (data control) | not a UI control in React | the API call replaces it; controls bound to it become controlled inputs fed by `useQuery` |
| `Image` / `PictureBox` | `<img>` | for static images; for dynamic drawing, `<canvas>` |
| `Timer` | `useEffect` + `setInterval` | with cleanup in the return |
| `Menu` (form menu bar) | sidebar nav, top bar, or nested route | depends on app style |
| `MDIForm` (parent for child forms) | a `<Layout>` route with nested `<Outlet>` | child VB6 forms become routes under the layout |
| `vbModal` modal `Form.Show vbModal` | a `<Dialog>` component (controlled by parent state) | not the browser's `alert()` — that blocks UI thread |

## Events

| VB6 event | React equivalent |
|---|---|
| `Form_Load` | initial `useEffect(() => { ... }, [])` |
| `Form_Unload` | cleanup in `useEffect` return + react-router unmount |
| `<Control>_Click` | `onClick` handler |
| `<Control>_Change` | `onChange` (for inputs) |
| `<Control>_KeyPress` | `onKeyDown` / `onKeyPress` |
| `<Control>_GotFocus` | `onFocus` |
| `<Control>_LostFocus` | `onBlur` |
| `<Control>_DblClick` | `onDoubleClick` |

## Modal dialogs (`vbModal`)

The VB6 pattern:

```vb
SomeForm.Show vbModal
' execution pauses until SomeForm is unloaded
```

In React, use a controlled `<Dialog>` component. The parent owns state:

```tsx
const [editing, setEditing] = useState<Book | 'new' | null>(null)
// ...
{editing && <BookEditor initial={editing === 'new' ? null : editing} onClose={() => setEditing(null)} />}
```

Don't try to make the dialog "block" — just hide everything else with a backdrop and let it `onClose` to re-show the parent. (This is what the seed library app's `<Dialog>` component does; reuse it.)

## MSFlexGrid → `<DataGrid>`

The seed library app already has a reusable `<DataGrid>` (`frontend/src/components/DataGrid.tsx`). It's a thin `<table>` wrapper that takes:

- `rows: T[]`
- `columns: { header, cell, width? }[]`
- `rowKey: (row) => string | number`
- `actions?: (row) => ReactNode` for per-row buttons

For any VB6 grid form, the translation is:

1. Identify the source SQL (in `.frm` form load or button click).
2. Make it an API endpoint returning `T[]`.
3. Render a page with `useQuery(...) → <DataGrid rows={data} columns={…} actions={…} />`.

## Data-bound controls (MSADODC + bound TextBox)

The pattern in VB6:

```vb
Adodc1.RecordSource = "select * from book1 where id = " & SearchID
Adodc1.Refresh
' TextBox controls bound via DataField/DataSource auto-update
```

Don't try to replicate two-way binding. Instead:

1. Fetch via `useQuery({ queryKey: ['book', id], queryFn: () => api.get(`/api/books/${id}`) })`.
2. Render values into controlled inputs.
3. On submit, send via `useMutation` (POST/PUT) and `invalidateQueries` to refresh.

This is what `BooksPage.tsx` does.

## Layout

VB6 forms use absolute coordinates. The React equivalent is **flexbox or CSS grid**, not absolutely-positioned divs. A typical pattern:

- Page header: `.toolbar` (flex row, title + actions)
- List view: `<DataGrid>`
- Detail/edit: `<Dialog>` containing a `.form-grid` (CSS grid of `<label>` + `<input>` pairs)

Look at `BooksPage.tsx` and `MembersPage.tsx` in the seed library app for the canonical structure.
