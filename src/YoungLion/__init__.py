# __init__.py
"""
YoungLion - Professional Python Library
Version: 0.0.9.9 - Major DataModel Expansion

A comprehensive library featuring:
- DDM (Dynamic Data Model): Hierarchical structured data management
- Range, Vector, Timeline, Dataset: Specialized DDM-based utilities
- SmartCache: Ultra-fast template-based data completion
- File operations, search, games, terminal styling, debugging tools
"""

__version__ = "0.0.9.9"
__author__ = "Cavanşir Qurbanzadə"
__author_email__ = "cavanshirpro@gmail.com"
__url__ = "https://github.com/cavanshirpro/YoungLion"

author = {
    'name': "Cavanşir",
    'surname': "Qurbanzadə",
    'username': "cavanshirpro",
    'email': "cavanshirpro@gmail.com"
}

# Import all public modules
from .function import *
from .search import *
from .DataModel import *
from .Colors import *

__all__ = [
    'DDM',
    'Range',
    'Vector',
    'Timeline',
    'Dataset',
    'SmartCache',
    'DDMBuilder',
    'Colors',
    'File',
    'SearchFile',
]