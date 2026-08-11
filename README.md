# YoungLion 0.1.0 — Real-life examples

This archive is intentionally separate from the main repository tree. It contains **70 standalone mini-projects** showing realistic ways to use YoungLion 0.1.0.

## How to use

Install/build YoungLion first, then enter any numbered folder and run `python main.py`. The examples require no third-party runtime dependencies beyond YoungLion itself. Network-facing features are demonstrated without sending real network traffic.

## Index

- [01. User profile with DDM](01_user_profile_ddm/README.md) — Model a user profile that is easy to access as attributes while remaining serializable.
- [02. Nested application settings](02_nested_settings_ddm/README.md) — Keep a nested settings object and update only one dotted path.
- [03. JSON state round-trip](03_ddm_json_state/README.md) — Serialize local state and recreate a DDM from JSON.
- [04. Frozen permission cache key](04_frozen_permission_key/README.md) — Use immutable DDM values as stable cache keys.
- [05. Identity-based live sessions](05_identity_session_set/README.md) — Keep mutable session objects in a Python set without value-hash problems.
- [06. Packed product catalog](06_packed_product_catalog/README.md) — Store many mostly-read product records using PackedDDM.
- [07. Registration validation](07_schema_registration/README.md) — Validate incoming user data with SchemaDDM.
- [08. Default feature flags](08_default_feature_flags/README.md) — Create missing feature flags lazily with a default factory.
- [09. Lazy invoice totals](09_lazy_invoice_totals/README.md) — Compute an expensive derived field only when first requested.
- [10. Zero-copy configuration view](10_zero_copy_config_view/README.md) — Wrap an existing dictionary without copying it.
- [11. Temperature range validator](11_temperature_range/README.md) — Use Range for clamping and normalization in sensor logic.
- [12. Game velocity vector](12_game_velocity_vector/README.md) — Perform common 2D/3D vector operations.
- [13. Release milestone timeline](13_release_timeline/README.md) — Represent product milestones on a timeline.
- [14. Small sales dataset report](14_sales_dataset/README.md) — Use Dataset for lightweight rows, grouping and statistics.
- [15. Responsive image sizing](15_ui_size_fit/README.md) — Fit a large size inside a target viewport.
- [16. Map point distance](16_map_point_distance/README.md) — Compute 2D distances and midpoints.
- [17. Theme color contrast](17_theme_color_contrast/README.md) — Evaluate UI color contrast and blending.
- [18. Matrix transformation](18_matrix_transform/README.md) — Use Matrix and Vector for small transformation math.
- [19. Category tree navigation](19_category_tree/README.md) — Build and traverse a product category tree.
- [20. API payload defaults](20_smartcache_api_defaults/README.md) — Complete many partial API payloads with a reusable template.
- [21. Programmatic request builder](21_ddm_builder_request/README.md) — Build a nested DDM from fluent builder steps.
- [22. Bulk product price update](22_listddm_price_update/README.md) — Update thousands-style records with path-native numeric operations.
- [23. Single-pass score normalization](23_batchplan_user_scores/README.md) — Combine several bulk mutations into one BatchPlan execution.
- [24. Unique account registry](24_setddm_unique_accounts/README.md) — Use SetDDM with a primary-key path.
- [25. Keyed user registry](25_dictddm_registry/README.md) — Use DictDDM as an application registry plus bulk operations.
- [26. Inventory table](26_ddmtable_inventory/README.md) — Select/query/assign over tabular DDM rows.
- [27. Group customers by country](27_group_customer_country/README.md) — Create groups and counts without hand-written loops.
- [28. Partition job queue](28_partition_job_queue/README.md) — Split jobs into ready and waiting sets.
- [29. Leaderboard selection](29_top_game_scores/README.md) — Use top/nth operations for a game leaderboard.
- [30. Bulk schema path refactor](30_bulk_path_refactor/README.md) — Rename/copy/delete paths across a whole collection.
- [31. Indexed exact user lookup](31_ddm_exact_user_search/README.md) — Create a reusable hash-style index for a nested DDM path.
- [32. Indexed age range search](32_ddm_age_range_search/README.md) — Use a numeric nested-path index for range lookup.
- [33. Fuzzy customer name search](33_ddm_fuzzy_name_search/README.md) — Search misspelled names without scanning custom Python logic.
- [34. Composite order index](34_ddm_composite_orders/README.md) — Index a frequently repeated combination such as country + status.
- [35. Settings search backend](35_application_settings_search/README.md) — Build a search box backend for application settings.
- [36. Product catalog search](36_product_catalog_search/README.md) — Rank product text and filter with structured fields.
- [37. Command palette autocomplete](37_command_palette_autocomplete/README.md) — Offer weighted prefix suggestions for a desktop app.
- [38. BM25 knowledge-base search](38_bm25_knowledge_articles/README.md) — Rank longer support articles using an inverted index and BM25.
- [39. Fuzzy contact matching](39_fuzzy_contact_match/README.md) — Compare user-entered names with multiple native fuzzy metrics.
- [40. Multi-keyword moderation scan](40_multi_pattern_moderation/README.md) — Scan text for many phrases in one search structure.
- [41. Nearest product prices](41_numeric_price_finder/README.md) — Use NumericSearch for range/nearest lookups.
- [42. Structured employee directory](42_structured_employee_search/README.md) — Search mapping records without creating custom document objects.
- [43. Search project filenames](43_file_name_search/README.md) — Index filenames below a directory and find relevant paths.
- [44. Search local notes by content](44_file_content_search/README.md) — Index text content inside files.
- [45. Faceted help-center search](45_search_faceted_help_center/README.md) — Search help pages and count result categories.
- [46. Crash-resistant JSON configuration](46_atomic_json_configuration/README.md) — Persist settings with an atomic replacement workflow.
- [47. Small CSV customer database](47_csv_customer_database/README.md) — Write, append, read and update CSV rows.
- [48. INI desktop settings](48_ini_desktop_settings/README.md) — Read and update classic INI configuration.
- [49. Java-style properties config](49_properties_service_config/README.md) — Manage a simple properties file without another dependency.
- [50. XML order export](50_xml_export/README.md) — Export a nested mapping to XML and read it back.
- [51. Dependency-free YAML config](51_yaml_app_config/README.md) — Use the practical YAML helper for simple application settings.
- [52. Backup with integrity check](52_backup_and_checksum/README.md) — Create a backup and compare checksums.
- [53. Chunked large-file processing](53_large_file_chunk_processing/README.md) — Process a large text file without reading all bytes at once.
- [54. Directory audit report](54_directory_audit/README.md) — Discover files and calculate metadata/checksums.
- [55. Binary artifact comparison](55_binary_file_compare/README.md) — Write binary blobs and compare exact contents.
- [56. ScriptRunner build step](56_script_runner_build_step/README.md) — Run a child Python script and capture a structured result.
- [57. Scheduled cleanup job](57_scheduler_cleanup_job/README.md) — Schedule a short in-process cleanup task and inspect its state.
- [58. Rotating application logger](58_rotating_application_logger/README.md) — Write structured contextual logs with local rotation settings.
- [59. Event-driven order flow](59_eventbus_order_flow/README.md) — Connect application components with prioritized event listeners.
- [60. TTL API response cache](60_ttlcache_api_response/README.md) — Cache computed responses locally with expiry and bounded size.
- [61. Rate-limited worker](61_rate_limited_worker/README.md) — Limit how fast a local worker performs an action.
- [62. Retry a transient operation](62_retry_transient_operation/README.md) — Retry a safe transient operation with backoff.
- [63. Circuit breaker around a service](63_circuit_breaker_service/README.md) — Stop repeated calls after a dependency keeps failing.
- [64. Article text analysis](64_text_article_analysis/README.md) — Compute common content metrics and extract entities.
- [65. Terminal status dashboard](65_terminal_status_dashboard/README.md) — Render a dependency-free CLI table and progress bar.
- [66. CLI color theme](66_cli_color_theme/README.md) — Use true color and ANSI-safe wrapping for a CLI.
- [67. E-mail report builder](67_email_report_builder/README.md) — Build a multipart e-mail locally without sending network traffic.
- [68. Local file-transfer workflow](68_local_file_transfer/README.md) — Use FileTransferManager status tracking without network access.
- [69. Mini product search service](69_full_product_search_service/README.md) — Combine DDM records, indexed nested fields, general text search and atomic persistence.
- [70. Local knowledge-base mini app](70_local_knowledge_base/README.md) — Combine file content indexing, text analysis, cache and application search into a local knowledge tool.

## Categories

- **01–21:** DDM, variants, model helpers and SmartCache/Builder.
- **22–30:** DDM collections and bulk algorithms.
- **31–45:** DDM/general/application search.
- **46–55:** File and structured format workflows.
- **56–68:** Script, scheduler, logger, events, cache/resilience, terminal/text/e-mail/transfer utilities.
- **69–70:** Combined mini applications.

Each folder is independent; inspect its README before adapting it to production.
