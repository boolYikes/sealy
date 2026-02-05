![Sealy CI](https://github.com/boolYikes/sealy/actions/workflows/main.yaml/badge.svg?branch=main)

## Infra
- FastAPI
### API Hosting
- Google Cloud Run: scales to zero on idle, cheap, handle quite a lot of reqs
- Google Compute Engine
- Cloudflare
### DB Hostings
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

### Project structure
- `db` for db models, `schemas` for pydantic api shape
- `sealy` for source code, `tests` for tests

--------
Run migration tests on a fresh DB, not reused one
Keep schema tests read-only
API tests should treat DB as a black box
Use markers e.g.,:
	@pytest.mark.integration
	@pytest.mark.api
----
- the rut
1. Init Alembic (once)
2. Define model
3. Generate revision (alembic revision --autogenerate) i.e., **humans generate migration**
4. Run pytest (migration tests apply upgrade head) i.e., In the CI, validate migration
5. Change model (schema evolution)
6. Generate new revision
7. Run pytest again
8. ...
**Clean your local dev db too!!** -> op.create_table must exist in the migration plan
**Include `op.execute("CREATE EXTENSION IF NOT EXISTS citext")` in the init migration**

### TODO
- Project layout to use src/