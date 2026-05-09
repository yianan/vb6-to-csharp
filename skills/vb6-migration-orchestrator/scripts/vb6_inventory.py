#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


CONTROL_RE = re.compile(r"^\s*Begin\s+([\w.]+)\s+(\w+)", re.IGNORECASE)
EVENT_RE = re.compile(r"^\s*(?:Private|Public)\s+Sub\s+(\w+_\w+)\s*\(", re.IGNORECASE)
FUNC_RE = re.compile(r"^\s*(?:Private|Public)\s+(?:Sub|Function)\s+(\w+)", re.IGNORECASE)
SQL_RE = re.compile(r'\b(?:rs\.Open|con\.Execute|Connection\.Execute)\s+(.+)', re.IGNORECASE)
SQL_ASSIGN_RE = re.compile(r'^\s*(?:SQL|sql)\s*=\s*(.+)$', re.MULTILINE)
SHOW_RE = re.compile(r"\b(\w+)\.Show\b", re.IGNORECASE)
GLOBAL_RE = re.compile(r"^\s*Public\s+(\w+)\s+As\s+(.+)$", re.IGNORECASE)
SKIP_DIRS = {".git", ".claude", ".codex", "node_modules", "bin", "obj", "backend", "frontend", "Migrations"}


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


def parse_vbp(path: Path) -> dict:
    project = {"name": path.stem, "startup_form": None, "forms": [], "modules": [], "classes": [], "references": [], "ocx_objects": []}
    for line in read_text(path).splitlines():
        if line.startswith("Startup="):
            project["startup_form"] = line.split("=", 1)[1].strip()
        elif line.startswith("Form="):
            project["forms"].append(line.split("=", 1)[1].strip())
        elif line.startswith("Module="):
            project["modules"].append(line.split("=", 1)[1].strip())
        elif line.startswith("Class="):
            project["classes"].append(line.split("=", 1)[1].strip())
        elif line.startswith("Reference="):
            project["references"].append(line.split("=", 1)[1].strip())
        elif line.startswith("Object="):
            project["ocx_objects"].append(line.split(";", 1)[-1].strip())
    return project


def parse_form(path: Path) -> dict:
    text = read_text(path)
    controls = []
    for match in CONTROL_RE.finditer(text):
        controls.append({"type": match.group(1), "name": match.group(2)})
    events = EVENT_RE.findall(text)
    sql_queries = [m.group(1).strip() for m in SQL_RE.finditer(text)]
    sql_queries.extend(m.group(1).strip() for m in SQL_ASSIGN_RE.finditer(text))
    opens_forms = sorted(set(SHOW_RE.findall(text)))
    caption = None
    for line in text.splitlines()[:200]:
        if "Caption" in line and "=" in line:
            caption = line.split("=", 1)[1].strip().strip('"')
            break
    return {
        "name": path.stem,
        "path": str(path),
        "caption": caption,
        "controls": controls,
        "events": events,
        "sql_queries": sql_queries,
        "opens_forms": opens_forms,
    }


def parse_module(path: Path) -> dict:
    text = read_text(path)
    globals_ = []
    functions = []
    sql_queries = []
    for line in text.splitlines():
        if m := GLOBAL_RE.match(line):
            globals_.append({"name": m.group(1), "type": m.group(2).strip()})
        if m := FUNC_RE.match(line):
            functions.append(m.group(1))
        if m := SQL_RE.search(line):
            sql_queries.append(m.group(1).strip())
        elif m := SQL_ASSIGN_RE.match(line):
            sql_queries.append(m.group(1).strip())
    return {"name": path.name, "path": str(path), "globals": globals_, "functions": functions, "sql_queries": sql_queries}


def iter_source_files(root: Path, suffix: str) -> list[Path]:
    files = []
    for path in root.rglob(f"*{suffix}"):
        if any(part in SKIP_DIRS or part.startswith(".") for part in path.relative_to(root).parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def infer_smells(forms: list[dict], modules: list[dict], project: dict) -> list[str]:
    smells = []
    all_sql = [q for f in forms for q in f["sql_queries"]] + [q for m in modules for q in m["sql_queries"]]
    if any("&" in q or "+" in q for q in all_sql):
        smells.append("Possible SQL injection: SQL built with string concatenation")
    if any("ADODB.Connection" in g["type"] or "ADODB.Recordset" in g["type"] for m in modules for g in m["globals"]):
        smells.append("Global ADO connection/recordset state")
    if any("login" in q.lower() and "password" in q.lower() for q in all_sql):
        smells.append("Likely plaintext password comparison in SQL")
    if any("MSFlexGrid" in c["type"] or "MSDataGrid" in c["type"] or "MSADODC" in c["type"] for f in forms for c in f["controls"]):
        smells.append("VB6 grid/data-bound controls need explicit React/API replacement")
    if project.get("ocx_objects"):
        smells.append("COM/OCX dependencies require replacement or explicit migration decision")
    return smells


def write_markdown(data: dict, path: Path) -> None:
    lines = [
        "# VB6 Inventory",
        "",
        f"Project: `{data['project'].get('name')}`",
        f"Startup form: `{data['project'].get('startup_form')}`",
        "",
        "## Forms",
        "",
        "| Form | Caption | Controls | Events | SQL queries |",
        "|---|---|---:|---:|---:|",
    ]
    for form in data["forms"]:
        lines.append(f"| `{form['name']}` | {form.get('caption') or ''} | {len(form['controls'])} | {len(form['events'])} | {len(form['sql_queries'])} |")
    lines.extend(["", "## Modules", ""])
    for module in data["modules"]:
        lines.append(f"- `{module['name']}`: {len(module['globals'])} globals, {len(module['functions'])} procedures, {len(module['sql_queries'])} SQL calls")
    lines.extend(["", "## External Dependencies", ""])
    for dep in data["external_dependencies"]:
        lines.append(f"- `{dep}`")
    lines.extend(["", "## Smells", ""])
    for smell in data["smells"]:
        lines.append(f"- {smell}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory a VB6 project.")
    parser.add_argument("root", type=Path)
    parser.add_argument("--out", type=Path, default=Path("docs"))
    args = parser.parse_args()

    root = args.root.resolve()
    out = args.out if args.out.is_absolute() else root / args.out
    out.mkdir(parents=True, exist_ok=True)

    vbp = next(root.glob("*.vbp"), None)
    project = parse_vbp(vbp) if vbp else {"name": root.name, "startup_form": None, "forms": [], "modules": [], "classes": [], "references": [], "ocx_objects": []}
    forms = [parse_form(p) for p in iter_source_files(root, ".frm")]
    modules = [parse_module(p) for p in iter_source_files(root, ".bas")]
    classes = [parse_module(p) for p in iter_source_files(root, ".cls")]
    external_dependencies = sorted(set(project.get("ocx_objects", [])))
    smells = infer_smells(forms, modules + classes, project)

    data = {
        "project": project,
        "forms": forms,
        "modules": modules,
        "classes": classes,
        "schema": {"tables": []},
        "external_dependencies": external_dependencies,
        "smells": smells,
    }
    (out / "vb6-inventory.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    write_markdown(data, out / "vb6-inventory.md")
    print(f"Wrote {out / 'vb6-inventory.json'}")
    print(f"Wrote {out / 'vb6-inventory.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
