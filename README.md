# YoungLion 0.1 — Advanced real-life examples

**Validation:** all 60 example entry points were exercised against the v0.1 source while preparing this pack; the API mismatches found during that pass were corrected before packaging.

This branch/package is deliberately separate from the library source tree. It contains **60 standalone mini-projects**, not 60 one-file API snippets. The first projects emphasize typed `class Something(DDM)` modeling and nested DDM composition; later projects cover high-volume collections, indexed search, files and integrated application services.

## How the examples are designed

- Every numbered directory has its own README and runnable `main.py`.
- Most non-trivial examples split models, repository/index ownership and services into separate files.
- DDM examples favor typed subclasses such as `User(DDM)` and `UserProfile(DDM)` while retaining DDM serialization/search/batch compatibility.
- Large-data examples generate enough records to demonstrate why indexing/batch APIs exist, while staying small enough to run locally.
- Examples avoid real credentials and network dependencies.

## Install

```bash
python -m pip install YoungLion==0.1.0
```

For pre-release development, install a local checkout of the `main` branch instead.

## Catalog

- [`01_typed_user_account/`](01_typed_user_account/) — Typed user account domain
- [`02_discord_guild_member/`](02_discord_guild_member/) — Discord-style guild member model
- [`03_ecommerce_order_domain/`](03_ecommerce_order_domain/) — E-commerce order domain
- [`04_game_player_profile/`](04_game_player_profile/) — Game player profile
- [`05_bank_account_domain/`](05_bank_account_domain/) — Bank account domain model
- [`06_api_response_models/`](06_api_response_models/) — Typed API response models
- [`07_application_settings_models/`](07_application_settings_models/) — Application settings model tree
- [`08_project_task_domain/`](08_project_task_domain/) — Project and task domain
- [`09_subscription_billing_domain/`](09_subscription_billing_domain/) — Subscription and billing domain
- [`10_product_inventory_domain/`](10_product_inventory_domain/) — Product inventory domain
- [`11_support_ticket_domain/`](11_support_ticket_domain/) — Support ticket domain
- [`12_media_library_domain/`](12_media_library_domain/) — Media library domain
- [`13_iot_device_domain/`](13_iot_device_domain/) — IoT device state domain
- [`14_student_course_domain/`](14_student_course_domain/) — Student/course profile domain
- [`15_audit_event_domain/`](15_audit_event_domain/) — Audit/security event domain
- [`16_schema_validated_signup/`](16_schema_validated_signup/) — Schema-validated signup pipeline
- [`17_default_feature_flags/`](17_default_feature_flags/) — DefaultDDM feature flag configuration
- [`18_lazy_invoice_totals/`](18_lazy_invoice_totals/) — LazyDDM invoice calculations
- [`19_frozen_permission_keys/`](19_frozen_permission_keys/) — FrozenDDM permission/cache keys
- [`20_identity_live_sessions/`](20_identity_live_sessions/) — IdentityDDM live session registry
- [`21_view_backed_settings/`](21_view_backed_settings/) — ViewDDM over shared mutable settings
- [`22_packed_large_catalog/`](22_packed_large_catalog/) — PackedDDM read-heavy catalog
- [`23_ddm_builder_request/`](23_ddm_builder_request/) — DDMBuilder request assembly
- [`24_tree_category_navigation/`](24_tree_category_navigation/) — TreeDDM category navigation
- [`25_geometry_and_matrix_models/`](25_geometry_and_matrix_models/) — Geometry and matrix helper models
- [`26_bulk_account_migration/`](26_bulk_account_migration/) — Bulk nested account migration
- [`27_batchplan_economy_rebalance/`](27_batchplan_economy_rebalance/) — Single-pass economy rebalance with BatchPlan
- [`28_typed_leaderboard/`](28_typed_leaderboard/) — Typed player leaderboard and nth selection
- [`29_setddm_unique_entities/`](29_setddm_unique_entities/) — SetDDM domain-key uniqueness
- [`30_dictddm_service_registry/`](30_dictddm_service_registry/) — DictDDM keyed service registry
- [`31_ddmtable_sales_analytics/`](31_ddmtable_sales_analytics/) — DDMTable analytics/reporting
- [`32_bulk_nested_profile_normalization/`](32_bulk_nested_profile_normalization/) — Bulk nested DDM callback normalization
- [`33_customer_segmentation/`](33_customer_segmentation/) — Customer segmentation with group/count/distinct
- [`34_chunked_job_processing/`](34_chunked_job_processing/) — Chunked batch job processing
- [`35_deduplicate_event_stream/`](35_deduplicate_event_stream/) — Event stream deduplication
- [`36_sorted_binary_lookup/`](36_sorted_binary_lookup/) — Sorted collection binary lookup
- [`37_bulk_path_refactor/`](37_bulk_path_refactor/) — Schema/path refactor across records
- [`38_inventory_restock_pipeline/`](38_inventory_restock_pipeline/) — Inventory restock bulk pipeline
- [`39_large_score_transform/`](39_large_score_transform/) — Large numeric transform and constraints
- [`40_index_invalidation_after_bulk_update/`](40_index_invalidation_after_bulk_update/) — Search index invalidation after bulk mutation
- [`41_indexed_user_directory/`](41_indexed_user_directory/) — Indexed typed user directory
- [`42_nested_age_range_search/`](42_nested_age_range_search/) — Nested numeric range search
- [`43_fuzzy_typed_name_search/`](43_fuzzy_typed_name_search/) — Fuzzy search over typed nested names
- [`44_composite_order_index/`](44_composite_order_index/) — Composite order index
- [`45_application_command_palette/`](45_application_command_palette/) — Application command palette backend
- [`46_product_catalog_backend/`](46_product_catalog_backend/) — Product catalog search backend
- [`47_bm25_knowledge_base/`](47_bm25_knowledge_base/) — BM25 knowledge base
- [`48_weighted_autocomplete_routes/`](48_weighted_autocomplete_routes/) — Weighted autocomplete for routes/actions
- [`49_numeric_price_index/`](49_numeric_price_index/) — Numeric range and nearest price search
- [`50_structured_employee_filters/`](50_structured_employee_filters/) — Structured employee filters
- [`51_aho_corasick_moderation/`](51_aho_corasick_moderation/) — Aho-Corasick multi-pattern moderation
- [`52_file_content_search_service/`](52_file_content_search_service/) — File name/content search service
- [`53_faceted_help_center/`](53_faceted_help_center/) — Faceted help-center backend
- [`54_large_ddm_search_repository/`](54_large_ddm_search_repository/) — Large DDM search repository
- [`55_hybrid_admin_search/`](55_hybrid_admin_search/) — Hybrid admin search service
- [`56_atomic_configuration_service/`](56_atomic_configuration_service/) — Atomic typed configuration service
- [`57_csv_etl_typed_ddm/`](57_csv_etl_typed_ddm/) — CSV ETL into typed DDM records
- [`58_resilient_local_job_runner/`](58_resilient_local_job_runner/) — Resilient local job runner
- [`59_event_cache_rate_pipeline/`](59_event_cache_rate_pipeline/) — Event-driven cached rate-limited pipeline
- [`60_full_local_catalog_application/`](60_full_local_catalog_application/) — Full local catalog mini-application

## Run all examples

```bash
python run_all.py
```

The runner executes every numbered `main.py` in an isolated subprocess and reports failures without requiring external services.
