# Testing applications using YoungLion

Use temporary directories for File tests, short scheduler delays plus `shutdown()`, mocked/local network endpoints for mail/FTP, and mutation-after-index tests for DDM search.

For fuzzy search, assert ordering/threshold behavior rather than fragile exact floating scores unless the scoring algorithm itself is being tested.
