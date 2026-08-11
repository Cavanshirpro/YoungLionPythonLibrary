from __future__ import annotations

import html as _html
import os
import re
import sqlite3
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Union

from .. import _native
from ._utilities import ScriptRunner

class FileExtraMixin:
    def _text_read(self, path: str) -> str: return self.txt_read_str(path)
    def _text_write(self, path: str, content: str, append: bool = False): _native.write_text(self._validate_and_prepare_path(path), str(content), append)
    md_read = _text_read
    rtf_read = _text_read
    html_read = _text_read
    css_read = _text_read
    js_read = _text_read
    tex_read = _text_read
    py_read = _text_read
    def md_write(self, path: str, content: str, append: bool = False): self._text_write(path, content, append)
    def rtf_write(self, path: str, content: str, append: bool = False): self._text_write(path, content, append)
    def html_write(self, path: str, content: str, append: bool = False): self._text_write(path, content, append)
    def css_write(self, path: str, content: str, append: bool = False): self._text_write(path, content, append)
    def js_write(self, path: str, content: str, append: bool = False): self._text_write(path, content, append)
    def tex_write(self, path: str, content: str): self._text_write(path, content, False)
    def tex_append(self, path: str, content: str): self._text_write(path, content, True)
    def py_write(self, path: str, content: str, append: bool = False): self._text_write(path, content, append)

    def handle_compressed(self, path: str, action: str, target: Optional[str] = None):
        action = action.lower()
        if action in {"compress", "zip"}:
            src = Path(self._validate_and_prepare_path(path)); dst = Path(self._validate_and_prepare_path(target or (str(src) + ".zip")))
            with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                if src.is_dir():
                    for item in src.rglob("*"):
                        if item.is_file(): zf.write(item, item.relative_to(src.parent))
                else: zf.write(src, src.name)
            return str(dst)
        if action in {"extract", "unzip"}:
            src = self._validate_and_prepare_path(path); dst = self._validate_and_prepare_path(target or str(Path(src).with_suffix("")))
            with zipfile.ZipFile(src, "r") as zf: zf.extractall(dst)
            return dst
        raise ValueError("action must be 'compress' or 'extract'")

    def sql_execute(self, path: str, query: str, params: Sequence[Any] = ()):
        fp = self._validate_and_prepare_path(path)
        with sqlite3.connect(fp) as con:
            cur = con.execute(query, tuple(params))
            rows = cur.fetchall() if cur.description else []
            con.commit()
            return rows

    @staticmethod
    def markdown_to_latex(markdown: str) -> str:
        text = str(markdown)
        text = re.sub(r"^###\s+(.+)$", r"\\subsubsection{\1}", text, flags=re.M)
        text = re.sub(r"^##\s+(.+)$", r"\\subsection{\1}", text, flags=re.M)
        text = re.sub(r"^#\s+(.+)$", r"\\section{\1}", text, flags=re.M)
        text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
        text = re.sub(r"(?<!\*)\*(.+?)\*(?!\*)", r"\\textit{\1}", text)
        text = re.sub(r"`(.+?)`", r"\\texttt{\1}", text)
        return text

    @staticmethod
    def latex_compile(content: str) -> str:
        text = re.sub(r"\\(?:section|subsection|subsubsection|textbf|textit|texttt)\{([^{}]*)\}", r"\1", str(content))
        text = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", text)
        text = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", text)
        text = text.replace("\\_", "_")
        return re.sub(r"\\[A-Za-z]+", "", text)

    @staticmethod
    def tex_to_markdown(content: str) -> str:
        text = re.sub(r"\\section\{([^{}]*)\}", r"# \1", str(content))
        text = re.sub(r"\\subsection\{([^{}]*)\}", r"## \1", text)
        text = re.sub(r"\\subsubsection\{([^{}]*)\}", r"### \1", text)
        text = re.sub(r"\\textbf\{([^{}]*)\}", r"**\1**", text)
        text = re.sub(r"\\textit\{([^{}]*)\}", r"*\1*", text)
        return text

    def latex_to_html(self, content: str, output_path: Optional[str] = None) -> str:
        body = f"<!doctype html><html><head><meta charset='utf-8'><script>MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']]}}}};</script><script defer src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script></head><body>\\({ _html.escape(content) }\\)</body></html>"
        if output_path: self.html_write(output_path, body)
        return body

    def latex_to_image(self, content: str, output_path: str) -> str:
        # Dependency-free vector fallback: emit SVG containing the TeX source as text.
        path = Path(self._validate_and_prepare_path(output_path))
        if path.suffix.lower() != ".svg": path = path.with_suffix(path.suffix + ".svg")
        escaped = _html.escape(content)
        svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='1200' height='120'><rect width='100%' height='100%' fill='white'/><text x='20' y='70' font-family='monospace' font-size='28' fill='black'>{escaped}</text></svg>"
        self.txt_write_str(str(path), svg)
        return str(path)

    def py_run(self, path: str, args: Optional[Sequence[str]] = None, terminal: bool = False) -> Optional[str]:
        fp = self._validate_and_prepare_path(path)
        cmd = [sys.executable, fp, *(str(x) for x in (args or []))]
        if terminal:
            return ScriptRunner(sys.executable).run_script(fp, inputs=args or [], terminal=True)
        return subprocess.run(cmd, text=True, capture_output=True, check=True).stdout

    def py_add_code(self, path: str, code: str, position: Union[str, int] = "end"):
        fp = self._validate_and_prepare_path(path)
        existing = self.txt_read_str(fp)
        if position == "end": new = existing + (("\n" if existing and not existing.endswith("\n") else "") + code)
        elif position == "start": new = code + ("\n" if code and not code.endswith("\n") else "") + existing
        elif isinstance(position, int):
            lines = existing.splitlines(True); idx = max(0, min(len(lines), position - 1)); lines.insert(idx, code + ("\n" if not code.endswith("\n") else "")); new = "".join(lines)
        else: raise ValueError("position must be 'start', 'end', or line number")
        self.txt_write_str(fp, new)

    def js_run(self, path: str, args: Optional[Sequence[str]] = None, terminal: bool = False) -> Optional[str]:
        return ScriptRunner("node").run_script(self._validate_and_prepare_path(path), inputs=args or [], terminal=terminal)


