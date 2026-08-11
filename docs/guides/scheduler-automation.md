# Scheduler and automation

`TaskScheduler` supports delayed/periodic in-process callbacks, priority metadata, pause/resume/cancel, retries, waiting and shutdown.

It is not a durable distributed job queue. Process termination loses in-memory scheduling state, so persist business-critical schedules separately when needed.
