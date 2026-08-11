# Manual PyPI publishing

1. Download the final release-bundle artifact from the GitHub Actions run.
2. Extract locally.
3. Validate the bundle/checksums.
4. Enter `pypi/`.
5. Run:

```bash
python -m twine check *
python -m twine upload *
```

Credentials stay on your own machine. Do not blindly upload `experimental/`.
