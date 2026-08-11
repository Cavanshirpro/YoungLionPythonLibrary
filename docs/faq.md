# FAQ

**Pure Python?** No; selected hot paths use C++17 through CPython C API.

**Runtime NumPy/PyYAML/Pillow/Paramiko?** No required third-party runtime packages.

**Why not everything C++?** Dynamic callbacks/application objects are often better Python APIs. Native code is used where benefit is clear.

**Which DDM?** Start with `DDM`; change variant for a semantic or measured reason.

**When index DDM data?** Repeated queries over enough records to repay index build/memory cost.

**Upload experimental wheels?** Not automatically. Validate and decide separately.
