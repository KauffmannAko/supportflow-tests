# supportflow-tests

**SupportFlow Test Repository** contains the QA assets for the SupportFlow API, including the test strategy, master test plan, Postman collection, and automated functional, integration, and end-to-end tests. It also includes CI/CD quality checks to continuously validate the API’s reliability, permissions, and core ticket-management workflows.

Click the links below to view the project QA documentation:

- **Test Strategy:** [View Test Strategy](https://docs.google.com/document/d/1SkFpEsAwOQgMsENwWr39IPVPW83ieOVd/edit?usp=sharing&ouid=113114915591322219906&rtpof=true&sd=true)
- **Master Test Plan:** [View Test plan](https://drive.google.com/file/d/1wsNON5vigljrWka66jySp0pM-b5-awT-/view?usp=sharing)
- **Permissions Matrix:** [View Permission Matrix](https://docs.google.com/spreadsheets/d/1WldexVC1D6NtY3bXDANP6NVenwBRSY5G/edit?usp=sharing&ouid=113114915591322219906&rtpof=true&sd=true)
- **E2E Flow Diagrams:**  [View simplied flow](https://drive.google.com/file/d/1pSCvLMLmk_irmPvdE2quzEpj17ub17Vt/view?usp=sharing) |
                          [View Detailed flow](https://drive.google.com/file/d/13t4yWVxuRvvS-MuHq-61d9dK29mprQTR/view?usp=sharing)

## Run the tests

Requires Docker running, Docker Compose v2 with `up --wait`, Make, and a POSIX
shell. Use an AMD64 runner for the published API image.

One-time setup: copy `.env.example` to `.env` and fill the four blank values
with a Django secret key, a dedicated non-root database user, its password,
and a MySQL root password. `.env` is ignored by Git. Single-quote secrets
containing `$` or `#`. Compose allows `api`, `localhost`, and `127.0.0.1`; no allowed-hosts setting is needed in `.env`.

To prepare the stack without executing tests:

```sh
make up
```

This validates configuration, pulls the API/MySQL images, builds the test image,
starts MySQL, waits for database readiness, runs migrations, and starts the API
with a readiness check. Containers remain running. Repeated runs reuse the
database and apply pending migrations. The published API image is never rebuilt.

Run the complete startup-and-test workflow with:

```sh
make test
# When finished:
make clean
```

This pulls `nanaako/supportflow-api:1.0.0` and MySQL, builds only the test image,
starts the database, runs migrations, starts the API, waits for readiness, and
runs pytest against `http://api:8000/api`. API and MySQL containers remain running
after success or failure. Repeated runs reuse the database until `make clean`
stops and removes containers, network, and database volume. Images and build
cache are retained. No host API or manual service startup is required.

For browser access, open `http://127.0.0.1:8000/api/health/` or
`http://127.0.0.1:8000/api/docs/`. The root `/` has no API route.

The published API image uses `/app` and starts with
`python manage.py runserver 0.0.0.0:8000`. Migrations run as
`python manage.py migrate --noinput` inside that image. Database and API
readiness each have a 120-second timeout; API readiness checks `/api/health/`.
The existing tests, framework, and Dockerfile are preserved.

Other commands remain available: `make config` validates configuration without
printing secrets; `make build` builds the test image; `make shell` opens its
shell; `make clean` stops and removes the stack and its database data. All
commands use the same default Compose project.

## CI and troubleshooting

Jenkins and GitHub Actions use the same `make test` command on an AMD64 runner
with Docker access. Inject `DJANGO_SECRET_KEY`, `DB_USER`, `DB_PASSWORD`, and
`MYSQL_ROOT_PASSWORD` through CI credentials/secrets; no `.env` file is needed.
Environment variables override `.env`. Test failures fail the job. The runner
preserves pytest's exit code; Make returns its own nonzero status for failed
recipes. Set a unique `COMPOSE_PROJECT_NAME` per concurrent CI job and use the
same value for testing and cleanup. Run `make clean` in a Jenkins `post { always }`
step or a GitHub Actions step with `if: always()`; cleanup is explicit.

- Docker connection failure: start Docker and check the active Docker context
  and runner access to the daemon.
- Missing credentials: fill the blank `.env` values or inject CI variables.
- Database or migration failure: inspect the service logs printed on failure;
  check credentials and use a non-root database user.
- API timeout or HTTP 400: check startup logs. Compose includes `api` in allowed
  hosts, and both tests and readiness checks use that hostname.
- Platform error: use AMD64 or configure AMD64 emulation.

Failures print service status and recent logs without stopping the stack.
Use `docker compose logs db api` to inspect it, then `make clean` when finished.

Runner checks without Docker:

```sh
python3 scripts/check-integration-runner.py
```
