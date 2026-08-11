from __future__ import annotations

import os
import platform
import sys

# std::filesystem is used by the native extension.  Older CPython macOS
# installers may default to a 10.9 deployment target, where libc++ does not
# expose the filesystem APIs we use.  Set a conservative floor before
# setuptools reads Python's build configuration.  cibuildwheel can still
# override this explicitly for a particular wheel.
if sys.platform == "darwin":
    _machine = platform.machine()
    _default_macos_target = "11.0" if _machine == "arm64" else "10.15"
    os.environ.setdefault("MACOSX_DEPLOYMENT_TARGET", _default_macos_target)
    # python.org installers can carry universal2 sysconfig flags even when a
    # developer only wants a native local build.  Prefer the host architecture
    # unless a wheel builder/user explicitly supplied ARCHFLAGS.
    if _machine in {"arm64", "x86_64"}:
        os.environ.setdefault("ARCHFLAGS", f"-arch {_machine}")

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
            macos_target = os.environ["MACOSX_DEPLOYMENT_TARGET"]
            compile_args += [f"-mmacosx-version-min={macos_target}"]
            link_args += ["-Wl,-dead_strip", f"-mmacosx-version-min={macos_target}"]
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
