#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for YoungLion library with platform-specific compilation support.

This script is used as a fallback and works alongside pyproject.toml for
setuptools-based installation. It automatically handles:
- Platform detection (Windows, Linux, macOS)
- Compilation of Python modules to binary (.pyd/.so)
- Binary wheel generation
- Cross-platform compatibility

Build commands:
    python setup.py build_ext --inplace     # Build extensions in-place
    python -m build                         # Build distributions using pyproject.toml
    python -m build --wheel                 # Build wheels for all platforms
    pip install -e .                        # Editable install
"""

import os
import sys
import platform
from setuptools import setup, find_packages
from setuptools.extension import Extension
from setuptools.dist import Distribution

# Read long description from README
with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Platform detection
system = platform.system()
machine = platform.machine()
is_windows = system == "Windows"
is_linux = system == "Linux"
is_macos = system == "Darwin"

# Dependencies with versions
REQUIREMENTS = [
    'PyYAML>=5.4',
    'PyPDF2>=2.0.0',
    'reportlab>=3.6.0',
    'Pillow>=8.0.0',
    'matplotlib>=3.3.0',
    'tqdm>=4.50.0',
    'paramiko>=2.7.0',
    'pylatexenc>=2.0',
    'markdown2>=2.3.0',
]

# Development dependencies
EXTRAS_REQUIRE = {
    'dev': [
        'pytest>=6.0',
        'pytest-cov>=2.10.0',
        'black>=21.0',
        'pylint>=2.8.0',
        'mypy>=0.9',
        'build>=0.10.0',
        'twine>=4.0.0',
    ],
}

# Package metadata
NAME = 'YoungLion'
VERSION = '0.0.9.9'
DESCRIPTION = "Professional Python library with hierarchical data models (DDM), utilities, games, file operations, search, terminal styling, and debugging tools for developers."
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
AUTHOR = "Cavanşir Qurbanzadə"
AUTHOR_EMAIL = "cavanshirpro@gmail.com"
MAINTAINER = "Cavanşir Qurbanzadə"
MAINTAINER_EMAIL = "cavanshirpro@gmail.com"
LICENSE = 'MIT'
KEYWORDS = 'YoungLion, Young Lion, DDM, DataModel, utilities, games, file-operations, terminal-styling, debugging, search'
URL = 'https://github.com/cavanshirpro/YoungLion'
PROJECT_URLS = {
    'Bug Tracker': 'https://github.com/cavanshirpro/YoungLion/issues',
    'Documentation': 'https://github.com/cavanshirpro/YoungLion#readme',
    'Source Code': 'https://github.com/cavanshirpro/YoungLion',
}

def get_platform_specific_settings():
    """
    Get platform-specific compiler settings and extension options.
    
    Returns:
        dict: Platform-specific settings for compilation
    """
    settings = {
        'extra_compile_args': [],
        'extra_link_args': [],
    }
    
    if is_windows:
        settings['extra_compile_args'] = ['/O2', '/W3']
        settings['extra_link_args'] = []
    elif is_linux:
        settings['extra_compile_args'] = ['-O3', '-march=native', '-fPIC']
        settings['extra_link_args'] = []
    elif is_macos:
        settings['extra_compile_args'] = ['-O3', '-march=native', '-fPIC']
        settings['extra_link_args'] = ['-mmacosx-version-min=10.9']
    
    return settings

def get_extensions():
    """
    Define C/Cython extensions for compilation.
    
    Pure Python modules (like YoungLion) typically don't need extensions,
    but this structure is provided for future optimization with Cython.
    
    Returns:
        list: List of Extension objects
    """
    extensions = []
    
    # Platform-specific settings
    platform_settings = get_platform_specific_settings()
    
    # Future: Add Cython-compiled modules here for performance
    # Example structure:
    # extensions.append(Extension(
    #     'YoungLion.data_model_fast',
    #     ['src/YoungLion/data_model_fast.pyx'],
    #     **platform_settings
    # ))
    
    return extensions

class CustomDistribution(Distribution):
    """Custom distribution class with platform-specific options."""
    pass

# Build configuration
setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    url=URL,
    project_urls=PROJECT_URLS,
    license=LICENSE,
    keywords=KEYWORDS,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    ext_modules=get_extensions(),
    distclass=CustomDistribution,
    python_requires='>=3.7',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Natural Language :: Turkish",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Topic :: Games/Entertainment",
        "Topic :: Office/Business",
        "Topic :: System :: Monitoring",
        "Typing :: Typed",
    ],
)

if __name__ == "__main__":
    print(f"\n{'='*70}")
    print(f"YoungLion Setup - Version {VERSION}")
    print(f"{'='*70}")
    print(f"Platform: {system} ({machine})")
    print(f"Python Version: {sys.version}")
    print(f"{'='*70}\n")