#!/usr/bin/env python3
"""Dependency-free structural audit for YoungLion's public Python type stubs.

This is deliberately a structural check, not a full static type checker. It verifies that:
- every .pyi parses on the running Python,
- each direct public class/function in the maintained Python modules exists in its paired .pyi,
- each direct public method defined on those classes exists in the stub class,
- py.typed exists,
- the two application-facing search aliases are declared in search.pyi.

Run from the repository root:
    python tools/check_stub_coverage.py
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "YoungLion"

PAIRS = [
    (SRC / "DataModel" / "_core.py", SRC / "DataModel" / "_core.pyi"),
    (SRC / "DataModel" / "_variants.py", SRC / "DataModel" / "_variants.pyi"),
    (SRC / "DataModel" / "_collections.py", SRC / "DataModel" / "_collections.pyi"),
    (SRC / "DataModel" / "_models.py", SRC / "DataModel" / "_models.pyi"),
    (SRC / "DataModel" / "_cache.py", SRC / "DataModel" / "_cache.pyi"),
    (SRC / "function" / "_base.py", SRC / "function" / "_base.pyi"),
    (SRC / "function" / "_formats.py", SRC / "function" / "_formats.pyi"),
    (SRC / "function" / "_extra.py", SRC / "function" / "_extra.pyi"),
    (SRC / "function" / "_utilities.py", SRC / "function" / "_utilities.pyi"),
    (SRC / "search.py", SRC / "search.pyi"),
    (SRC / "Colors.py", SRC / "Colors.pyi"),
]

@dataclass(frozen=True)
class ModuleSurface:
    functions: set[str]
    classes: dict[str, set[str]]


def parse(path: Path) -> ast.Module:
    try:
        return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        raise SystemExit(f"[stub-audit] syntax error in {path}: {exc}") from exc


def surface(tree: ast.Module) -> ModuleSurface:
    functions: set[str] = set()
    classes: dict[str, set[str]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            functions.add(node.name)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            methods = {
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and not child.name.startswith("_")
            }
            classes[node.name] = methods
    return ModuleSurface(functions, classes)


def declared_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def main() -> int:
    errors: list[str] = []
    pyi_files = sorted(SRC.rglob("*.pyi"))
    for pyi in pyi_files:
        parse(pyi)

    if not (SRC / "py.typed").is_file():
        errors.append("missing src/YoungLion/py.typed")

    checked_methods = 0
    checked_classes = 0
    checked_functions = 0
    for source_path, stub_path in PAIRS:
        src = surface(parse(source_path))
        stub = surface(parse(stub_path))
        checked_functions += len(src.functions)
        checked_classes += len(src.classes)
        for name in sorted(src.functions - stub.functions):
            errors.append(f"{source_path.relative_to(ROOT)}: public function {name!r} missing from {stub_path.name}")
        for class_name, methods in sorted(src.classes.items()):
            if class_name not in stub.classes:
                errors.append(f"{source_path.relative_to(ROOT)}: public class {class_name!r} missing from {stub_path.name}")
                continue
            checked_methods += len(methods)
            missing = methods - stub.classes[class_name]
            for method in sorted(missing):
                errors.append(f"{source_path.relative_to(ROOT)}: {class_name}.{method} missing from {stub_path.name}")

    search_stub = declared_names(parse(SRC / "search.pyi"))
    for alias in ("SearchEngine", "DDMIndex"):
        if alias not in search_stub:
            errors.append(f"search.pyi: missing public alias {alias}")

    if errors:
        print("[stub-audit] FAILED")
        for error in errors:
            print(f" - {error}")
        return 1

    print(
        "[stub-audit] OK — "
        f"{len(pyi_files)} stub files parsed; "
        f"{checked_classes} public classes, {checked_methods} direct public methods, "
        f"{checked_functions} module-level public functions structurally covered."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
