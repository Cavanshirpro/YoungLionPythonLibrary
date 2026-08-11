# Utilities API

- `ScriptRunner` + `CommandResult`: subprocess execution, cwd/env/input/timeout/check/capture, interpreter detection and async process start.
- `TaskScheduler` + `TaskInfo`: delays, repeats, pause/resume/cancel, retries, wait/inspection/shutdown.
- `Logger`: structured context, levels, console/file output, rotation.
- `EmailManager`: EmailMessage construction, HTML, CC/BCC, attachments, SMTP and inbox helper.
- `FileTransferManager`: local/FTP transfers with IDs/status/progress.
- `TextProcessor`: counts, positions, replace, n-grams, extract URLs/e-mails, summarize, similarity/readability/stats.
- `EventBus`, `TTLCache`, `RateLimiter`, `RetryPolicy`, `CircuitBreaker`, `Stopwatch`.
