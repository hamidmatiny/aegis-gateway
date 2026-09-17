# Audit log

## 2026-09-17T16:46Z — hire-day seed audit (pre-deploy, from monorepo tip)

- Inventory: 12 files, 9 Go, **3** `*_test.go` (main, pipeline, auth).
- README known gaps still open: gRPC GatewayService (proto only), OTel hot path, audit aggregation not from gateway, single shared http.Client.
- **Stale cross-doc:** `model-router/README.md` still claims "Gateway orchestration is future work" while `gateway/README.md` documents live pipeline calling model-router — docs PR for model-router owner; gateway owner should verify pipeline.go matches README diagram.
- First task: expand pipeline failure-path tests; confirm `/v1/tools/evaluate` → agent-gate path still wired.
