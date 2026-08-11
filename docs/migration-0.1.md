# Migration to 0.1

0.1 keeps historical top-level imports while reorganizing internals and moving hot paths native.

Key changes: Python floor 3.10; zero required runtime third-party dependencies; expanded DDM variants/collections/search/File; PEP 561 stubs; narrower dependency-free behavior for advanced PDF/YAML/SFTP use cases.

Test old applications especially where they relied on third-party packages that were previously imported by YoungLion.
