# Production checklist

Use this list before integrating YoungLion into a production application.

## Data model

- Choose the DDM variant intentionally.
- Validate untrusted structured input with a schema or application-specific checks.
- Decide whether missing paths are errors or should return defaults.
- Keep mutable value objects out of native Python hash containers unless using an identity/frozen variant designed for that purpose.

## Search

- Build indexes only for repeated query paths.
- Define index invalidation after mutations.
- Keep a scan fallback for small/one-shot data when appropriate.
- Set query/result limits for user-facing fuzzy search.
- Normalize case/token rules consistently.
- Benchmark ranking with representative documents, not synthetic single-word strings only.

## Files

- Use atomic writes for important configuration/state.
- Verify backups/checksums before deleting the original.
- Treat paths from untrusted users as untrusted input.
- Do not assume practical YAML or basic PDF helpers implement every advanced feature of those ecosystems.

## Concurrency

- Read the thread-safety reference for each shared utility.
- Do not assume Python callbacks become parallel simply because collection traversal is native.
- Shut down scheduler/background resources cleanly.

## Resilience

- Retry only operations that are safe to retry.
- Set finite retry counts and timeouts.
- Use circuit breakers for repeatedly failing external dependencies.
- Rate-limit at the appropriate resource boundary.

## Packaging

- Run strict native build and tests.
- Run `tools/check_stub_coverage.py`.
- Build both sdist and wheels.
- Test a wheel in a fresh environment with `--no-deps`.
- Inspect `Requires-Dist` metadata.
- Run `twine check` before manual publication.
- Publish only the stable `pypi/` release-bundle directory, not `experimental/` artifacts.
