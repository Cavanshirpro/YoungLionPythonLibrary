from __future__ import annotations

import os
import sys
from setuptools import Extension, setup

DEBUG = os.environ.get("YOUNGLION_NATIVE_DEBUG") == "1"
STRICT = os.environ.get("YOUNGLION_STRICT") == "1"
USE_LTO = os.environ.get("YOUNGLION_DISABLE_LTO") != "1" and not DEBUG

compile_args: list[str]
link_args: list[str] = []

if sys.platform == "win32":
    if DEBUG:
        compile_args = ["/std:c++17", "/Od", "/Zi", "/EHsc", "/permissive-"]
    else:
        compile_args = ["/std:c++17", "/O2", "/EHsc", "/permissive-", "/DNDEBUG", "/Gy", "/Gw"]
        if USE_LTO:
            compile_args += ["/GL"]
            link_args += ["/LTCG", "/OPT:REF", "/OPT:ICF"]
    if STRICT:
        compile_args += ["/W4", "/WX"]
else:
    if DEBUG:
        compile_args = ["-std=c++17", "-O0", "-g3"]
    else:
        compile_args = ["-std=c++17", "-O3", "-g0", "-DNDEBUG", "-fvisibility=hidden", "-ffunction-sections", "-fdata-sections"]
        if sys.platform.startswith("linux"):
            compile_args += ["-fno-semantic-interposition"]
            link_args += ["-Wl,--gc-sections"]
        if sys.platform == "darwin":
            link_args += ["-Wl,-dead_strip"]
        if USE_LTO:
            compile_args += ["-flto"]
            link_args += ["-flto"]
    if STRICT:
        compile_args += ["-Wall", "-Wextra", "-Wpedantic", "-Wno-cast-function-type", "-Werror"]

setup(
    ext_modules=[
        Extension(
            "YoungLion._native",
            sources=["src/YoungLion/_native.cpp"],
            language="c++",
            extra_compile_args=compile_args,
            extra_link_args=link_args,
        )
    ]
)
