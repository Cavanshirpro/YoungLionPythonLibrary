# Logging

`Logger` supports levels, file/console output, rotation and bound context.

```python
log = Logger("app.log", "INFO", max_bytes=2_000_000, backup_count=3)
log.bind(request_id="abc123").info("request started", method="GET")
```

For large deployments, feed/bridge these logs into the application's centralized observability platform.
