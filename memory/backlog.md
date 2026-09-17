# Starting backlog — day one

- First audit: coverage of pipeline.go + auth + API; reconcile README "Known limitations" (gRPC, OTel, audit aggregation, connection pooling) against current code.
- Stale-doc check: model-router README still says gateway orchestration is future work — gateway already calls model-router; open a docs PR if confirmed.
- Test gap: only 3 *_test.go files for 9 Go files — expand pipeline failure-path tests.
