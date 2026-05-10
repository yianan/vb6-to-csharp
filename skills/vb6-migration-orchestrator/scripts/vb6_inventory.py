#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


CONTROL_RE = re.compile(r"^\s*Begin\s+([\w.]+)\s+(\w+)", re.IGNORECASE)
EVENT_RE = re.compile(r"^\s*(?:Private|Public|Friend)?\s*Sub\s+(\w+_\w+)\s*\(", re.IGNORECASE)
FUNC_RE = re.compile(r"^\s*(?:Private|Public|Friend)?\s*(?:Sub|Function|Property)\s+(\w+)", re.IGNORECASE)
SQL_RE = re.compile(r'\b(?:rs\.Open|con\.Execute|Connection\.Execute)\s+(.+)', re.IGNORECASE)
SQL_ASSIGN_RE = re.compile(r'^\s*(?:SQL|sql)\s*=\s*(.+)$', re.MULTILINE)
SHOW_RE = re.compile(r"\b(\w+)\.Show\b", re.IGNORECASE)
GLOBAL_RE = re.compile(r"^\s*Public\s+(\w+)\s+As\s+(.+)$", re.IGNORECASE)
SKIP_DIRS = {".git", ".claude", ".codex", "node_modules", "bin", "obj", "backend", "frontend", "Migrations"}
SOURCE_EXTS = {".vbp", ".vbg", ".frm", ".bas", ".cls", ".ctl"}
DATA_EXTS = {".mdb", ".accdb", ".bak", ".db", ".sqlite", ".sqlite3"}
RESOURCE_EXTS = {".frx", ".res", ".ico", ".bmp", ".jpg", ".jpeg", ".png"}
BINARY_EXTS = {".exe", ".dll", ".ocx"}
RISK_PATTERNS = [
    "Declare Function",
    "Declare Sub",
    "CreateObject",
    "GetObject",
    "WithEvents",
    "On Error Resume Next",
    "On Error GoTo",
    "Resume Next",
    "Err.Number",
    "Err.Description",
    "Option Base",
    "LBound",
    "UBound",
    "ReDim Preserve",
    "ReDim",
    "Collection",
    "Variant",
    "App.Path",
    "Attribute VB_PredeclaredId = True",
]


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


def scan_risks(text: str) -> list[dict]:
    risks = []
    for number, line in enumerate(text.splitlines(), 1):
        lowered = line.lower()
        for pattern in RISK_PATTERNS:
            if pattern.lower() in lowered:
                risks.append({"line": number, "pattern": pattern})
    return risks


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
        "risk_hits": scan_risks(text),
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
    return {
        "name": path.name,
        "path": str(path),
        "globals": globals_,
        "functions": functions,
        "sql_queries": sql_queries,
        "risk_hits": scan_risks(text),
    }


def iter_source_files(root: Path, suffix: str) -> list[Path]:
    files = []
    for path in root.rglob(f"*{suffix}"):
        if any(part in SKIP_DIRS or part.startswith(".") for part in path.relative_to(root).parts[:-1]):
            continue
        files.append(path)
    return sorted(files)


def iter_files_by_ext(root: Path, extensions: set[str]) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in extensions:
            continue
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
    if any(".mdb" in q.lower() or ".accdb" in q.lower() for q in all_sql):
        smells.append("Access database dependency requires DAO/ADO export or EF Core schema mapping")
    if any(hit["pattern"] in {"On Error Resume Next", "On Error GoTo"} for item in forms + modules for hit in item.get("risk_hits", [])):
        smells.append("VB6 On Error control flow needs explicit characterization before porting")
    if any(hit["pattern"] in {"Option Base", "LBound", "UBound", "ReDim Preserve", "Collection"} for item in forms + modules for hit in item.get("risk_hits", [])):
        smells.append("Indexing/collection semantics may change during C# migration")
    return smells


def write_markdown(data: dict, path: Path) -> None:
    lines = [
        "# VB6 Inventory",
        "",
        f"Project: `{data['project'].get('name')}`",
        f"Startup form: `{data['project'].get('startup_form')}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in data.get("counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend([
        "",
        "## Forms",
        "",
        "| Form | Caption | Controls | Events | SQL queries |",
        "|---|---|---:|---:|---:|",
    ])
    for form in data["forms"]:
        lines.append(f"| `{form['name']}` | {form.get('caption') or ''} | {len(form['controls'])} | {len(form['events'])} | {len(form['sql_queries'])} |")
    lines.extend(["", "## Modules", ""])
    for module in data["modules"]:
        lines.append(f"- `{module['name']}`: {len(module['globals'])} globals, {len(module['functions'])} procedures, {len(module['sql_queries'])} SQL calls, {len(module.get('risk_hits', []))} risk hits")
    if data.get("data_files"):
        lines.extend(["", "## Data Files", ""])
        for file_path in data["data_files"]:
            lines.append(f"- `{file_path}`")
    if data.get("resource_files"):
        lines.extend(["", "## Resource Files", ""])
        for file_path in data["resource_files"]:
            lines.append(f"- `{file_path}`")
    if data.get("binaries"):
        lines.extend(["", "## Binary Artifacts", ""])
        for file_path in data["binaries"]:
            lines.append(f"- `{file_path}`")
    lines.extend(["", "## External Dependencies", ""])
    for dep in data["external_dependencies"]:
        lines.append(f"- `{dep}`")
    risk_items = [(item["path"], hit) for item in data["forms"] + data["modules"] + data["classes"] for hit in item.get("risk_hits", [])]
    if risk_items:
        lines.extend(["", "## Risk Hits", ""])
        for source_path, hit in risk_items[:80]:
            lines.append(f"- `{source_path}` line {hit['line']}: {hit['pattern']}")
        if len(risk_items) > 80:
            lines.append(f"- ... {len(risk_items) - 80} more risk hits in `vb6-inventory.json`")
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

    source_files = iter_files_by_ext(root, SOURCE_EXTS)
    project_files = [p for p in source_files if p.suffix.lower() == ".vbp"]
    project_group_files = [p for p in source_files if p.suffix.lower() == ".vbg"]
    projects = [parse_vbp(p) for p in project_files]
    project = projects[0] if projects else {"name": root.name, "startup_form": None, "forms": [], "modules": [], "classes": [], "references": [], "ocx_objects": []}
    forms = [parse_form(p) for p in iter_source_files(root, ".frm")]
    modules = [parse_module(p) for p in iter_source_files(root, ".bas")]
    classes = [parse_module(p) for p in iter_source_files(root, ".cls") + iter_source_files(root, ".ctl")]
    data_files = [str(p) for p in iter_files_by_ext(root, DATA_EXTS)]
    resource_files = [str(p) for p in iter_files_by_ext(root, RESOURCE_EXTS)]
    binaries = [str(p) for p in iter_files_by_ext(root, BINARY_EXTS)]
    external_dependencies = sorted(set(dep for parsed in projects for dep in parsed.get("ocx_objects", [])))
    smells = infer_smells(forms, modules + classes, project)

    data = {
        "project": project,
        "projects": projects,
        "project_groups": [str(p) for p in project_group_files],
        "counts": {
            "project_files": len(project_files),
            "project_groups": len(project_group_files),
            "forms": len(forms),
            "modules": len(modules),
            "classes_and_controls": len(classes),
            "data_files": len(data_files),
            "resource_files": len(resource_files),
            "binaries": len(binaries),
            "controls": sum(len(form["controls"]) for form in forms),
            "procedures": sum(len(item["functions"]) for item in modules + classes) + sum(len(form["events"]) for form in forms),
            "risk_hits": sum(len(item.get("risk_hits", [])) for item in forms + modules + classes),
        },
        "forms": forms,
        "modules": modules,
        "classes": classes,
        "schema": {"tables": []},
        "data_files": data_files,
        "resource_files": resource_files,
        "binaries": binaries,
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
