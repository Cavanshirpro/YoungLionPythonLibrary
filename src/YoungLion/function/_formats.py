from __future__ import annotations

import configparser
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple
import xml.etree.ElementTree as ET

from .. import _native

class FileFormatsMixin:
    def pdf_read(self, path: str) -> str:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp): raise FileNotFoundError(path)
        return _native.pdf_read(fp)

    def pdf_write(self, path: str, content: str):
        _native.pdf_write(self._validate_and_prepare_path(path), str(content))

    @staticmethod
    def _xml_to_dict(element: ET.Element) -> Any:
        if element.attrib.get("xsi:nil") == "true": return None
        text = (element.text or "").strip()
        if len(element) == 0:
            if element.attrib:
                out: Dict[str, Any] = {"@attributes": dict(element.attrib)}
                if text: out["#text"] = text
                return out
            return text if text else None
        result: Dict[str, Any] = {}
        if element.attrib: result["@attributes"] = dict(element.attrib)
        if text: result["#text"] = text
        for child in element:
            value = FileFormatsMixin._xml_to_dict(child)
            if child.tag in result:
                if not isinstance(result[child.tag], list): result[child.tag] = [result[child.tag]]
                result[child.tag].append(value)
            else:
                result[child.tag] = value
        return result

    @staticmethod
    def _dict_to_xml(data: Any, root_element: str) -> ET.Element:
        elem = ET.Element(root_element)
        if data is None:
            elem.set("xsi:nil", "true"); return elem
        if isinstance(data, list):
            for item in data: elem.append(FileFormatsMixin._dict_to_xml(item, root_element))
            return elem
        if not isinstance(data, Mapping):
            elem.text = str(data); return elem
        for k, v in data.get("@attributes", {}).items(): elem.set(str(k), str(v))
        if "#text" in data: elem.text = str(data["#text"])
        for key, value in data.items():
            if key in ("@attributes", "#text"): continue
            if isinstance(value, list):
                for item in value: elem.append(FileFormatsMixin._dict_to_xml(item, str(key)))
            else: elem.append(FileFormatsMixin._dict_to_xml(value, str(key)))
        return elem

    def xml_read(self, path: str) -> Optional[Dict[str, Any]]:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp): raise FileNotFoundError(path)
        root = ET.parse(fp).getroot()
        return self._xml_to_dict(root)

    def xml_write(self, path: str, data: Dict[str, Any], root_element: str = "root"):
        if not isinstance(data, dict): raise ValueError("Data to be written must be a dictionary.")
        ET.ElementTree(self._dict_to_xml(data, root_element)).write(self._validate_and_prepare_path(path), encoding="utf-8", xml_declaration=True)

    def xml_append(self, path: str, data: Dict[str, Any], root_element: str = "root"):
        if not isinstance(data, dict): raise ValueError("Data to be appended must be a dictionary.")
        fp = self._validate_and_prepare_path(path)
        if os.path.exists(fp): tree = ET.parse(fp); root = tree.getroot()
        else: root = ET.Element(root_element); tree = ET.ElementTree(root)
        root.append(self._dict_to_xml(data, root_element))
        tree.write(fp, encoding="utf-8", xml_declaration=True)

    def xml_find(self, path: str, query: str) -> Optional[Dict[str, Any]]:
        root = ET.parse(self._validate_and_prepare_path(path)).getroot()
        element = root.find(query)
        return None if element is None else self._xml_to_dict(element)

    def csv_read(self, path: str, delimiter: str = ',', quotechar: str = '"') -> List[Dict[str, str]]:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp): self.txt_write_str(fp, "")
        return _native.csv_read(fp, delimiter, quotechar)

    def csv_write(self, path: str, data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None, delimiter: str = ',', quotechar: str = '"'):
        return _native.csv_write(self._validate_and_prepare_path(path), data, fieldnames, delimiter, quotechar, False)

    def csv_append(self, path: str, data: List[Dict[str, str]], fieldnames: Optional[List[str]] = None, delimiter: str = ',', quotechar: str = '"'):
        return _native.csv_write(self._validate_and_prepare_path(path), data, fieldnames, delimiter, quotechar, True)

    def csv_update(self, path: str, data: List[Dict[str, str]], identifier: str, delimiter: str = ',', quotechar: str = '"'):
        rows = self.csv_read(path, delimiter, quotechar)
        updates = {str(row[identifier]): row for row in data if identifier in row}
        for row in rows:
            if identifier in row and str(row[identifier]) in updates: row.update(updates[str(row[identifier])])
        if rows: self.csv_write(path, rows, list(rows[0]), delimiter, quotechar)

    @staticmethod
    def _yaml_scalar(text: str) -> Any:
        text = text.strip()
        if not text: return ""
        lower = text.lower()
        if lower in {"null", "none", "~"}: return None
        if lower in {"true", "yes", "on"}: return True
        if lower in {"false", "no", "off"}: return False
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")): return text[1:-1]
        try: return int(text)
        except ValueError: pass
        try: return float(text)
        except ValueError: pass
        if text.startswith(("{", "[")):
            try: return _native.json_loads(text)
            except Exception: pass
        return text

    def yaml_read(self, path: str, default: Optional[dict] = None) -> dict:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp):
            self.yaml_write(path, default or {})
            return dict(default or {})
        text = self.txt_read_str(path)
        try:
            parsed = _native.json_loads(text)
            if isinstance(parsed, dict): return parsed
        except Exception: pass
        root: Dict[str, Any] = {}; stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]
        for raw in text.splitlines():
            if not raw.strip() or raw.lstrip().startswith("#"): continue
            indent = len(raw) - len(raw.lstrip(" "))
            line = raw.strip()
            if ":" not in line: continue
            key, value = line.split(":", 1); key = key.strip(); value = value.strip()
            while stack and indent <= stack[-1][0]: stack.pop()
            parent = stack[-1][1]
            if value:
                parent[key] = self._yaml_scalar(value)
            else:
                child: Dict[str, Any] = {}; parent[key] = child; stack.append((indent, child))
        if isinstance(default, dict): return self._recursive_update(root, default)
        return root

    def yaml_write(self, path: str, data: dict):
        if not isinstance(data, dict): raise TypeError("data must be dict")
        def emit(d: Mapping[str, Any], level: int = 0) -> List[str]:
            lines: List[str] = []
            for k, v in d.items():
                if isinstance(v, Mapping):
                    lines.append(" " * level + f"{k}:"); lines.extend(emit(v, level + 2))
                elif isinstance(v, bool): lines.append(" " * level + f"{k}: {'true' if v else 'false'}")
                elif v is None: lines.append(" " * level + f"{k}: null")
                elif isinstance(v, (list, tuple, dict)): lines.append(" " * level + f"{k}: {_native.json_dumps(v, indent=-1)}")
                else: lines.append(" " * level + f"{k}: {v}")
            return lines
        self.txt_write_str(path, "\n".join(emit(data)) + ("\n" if data else ""))

    def ini_read(self, path: str, default: Optional[Dict[str, Dict[str, str]]] = None) -> Dict[str, Dict[str, str]]:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp):
            _native.ini_write(fp, default or {}, False); return dict(default or {})
        data = _native.ini_read(fp)
        if default:
            for sec, vals in default.items(): data.setdefault(sec, {}).update({k: data.get(sec, {}).get(k, v) for k, v in vals.items()})
        return data

    def ini_write(self, path: str, data: Dict[str, Dict[str, str]], append: bool = False):
        fp = self._validate_and_prepare_path(path)
        if append and os.path.exists(fp):
            old = _native.ini_read(fp)
            for sec, vals in data.items(): old.setdefault(sec, {}).update(vals)
            data = old
            append = False
        _native.ini_write(fp, data, append)

    def properties_read(self, path: str) -> Dict[str, str]:
        fp = self._validate_and_prepare_path(path)
        if not os.path.exists(fp): self.txt_write_str(path, "")
        return _native.properties_read(fp)

    def properties_write(self, path: str, data: Dict[str, str], append: bool = False): _native.properties_write(self._validate_and_prepare_path(path), data, append)

