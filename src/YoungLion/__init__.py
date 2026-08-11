"""YoungLion - native-accelerated developer utility library."""

__version__ = "0.1.0"
__author__ = "Cavanşir Qurbanzadə"
__author_email__ = "cavanshirpro@gmail.com"
__url__ = "https://github.com/Cavanshirpro/YoungLionPythonLibrary"

author = {
    "name": "Cavanşir",
    "surname": "Qurbanzadə",
    "username": "cavanshirpro",
    "email": "cavanshirpro@gmail.com",
}

# Keep the historical import surface. DataModel/function resolve to the new
# packages, whose hot paths are backed by YoungLion._native (C++17).
from .function import *
try:
    from .search import *
except ImportError:
    pass
from .DataModel import *
try:
    from .Colors import *
except ImportError:
    pass
