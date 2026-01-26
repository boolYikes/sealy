## SLO
### API
- latency < 200ms
### DB
- < 1~3ms

## Infra
- FastAPI
### API Hosting
- Google Cloud Run: scales to zero on idle, cheap, handle quite a lot of reqs
- Google Compute Engine
- Cloudflare
### DB Hosting
- Run it on the same VM as API (warning, hands-on)
- Or use managed (expensive)
### Logging and Metrics
- Measure queries per endpoints

## DB Design
1. Schema design
   - correct pk
   - proper fk
   - avoid unncessary joins
   - don't over-normalize
2. Indexing
   - For every join, need index e.g., for `JOIN t1 ON t1.id = t2.id`, `INDEX ON t1(id)` is needed
3. Access patterns > theoretical purity
   - most frequented queries? -> optimize specifically for that. Analyze traffic
   - done with pre-join, materialized views, small denormalization
4. Connection management
   - use connection pool. don't open a new db connection **per request!**
5. Query count per request
   - one request should be 1 to 3 queries not ten something queries (worst case db latency 10ms -> must be < 200ms according to SLO)
   - no looped queries! let the query do the job

### Schema
- `db` for db models, `schemas` for pydantic api shape

--------
TDD
- Write failing test → implement → refactor
- If a test depends on DB it is not a unit test anymore!!!

DB init (migration) test
- App can start from empty DB
- Migrations run cleanly and idempotently
✔️ catches scary prod bugs early

Schema test
- DB schema matches expectations
- Tables/columns/indexes exist
✔️ especially good if using raw SQL / Alembic

Init pytest fixtures
- Session-scoped DB
- Transaction rollback per test
✔️ fast + clean

API test
- GraphQL / REST behaves correctly end-to-end
✔️ highest confidence
--------
Run migration tests on a fresh DB, not reused one
Keep schema tests read-only
API tests should treat DB as a black box
Use markers e.g.,:
	@pytest.mark.integration
	@pytest.mark.api
----
TODOs
1. setup (sqlalchemy, alembic, pytest)
2. proj structure
3. alchemy model definition
4. alembic env configured
5. migration test code (with an engine as fixture