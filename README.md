# Bookstore API tests

Automated tests for the public FakeRestAPI bookstore at `https://fakerestapi.azurewebsites.net`.

The suite covers the Books and Authors collections: list, get by id, create, update, and delete. It checks happy paths and the error cases the demo actually returns.

## Open this folder

In Visual Studio Code, choose **File → Open Folder** and select:

the `bookstore-api-tests` project folder containing this README.

You can also double-click `bookstore-api-tests.code-workspace`.

## Setup

Python 3.12 or newer is required. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Run the tests

```powershell
pytest
```

Useful variants:

```powershell
ruff check .
pytest -m unit
pytest -m "books or authors"
pytest -m books
pytest -m authors
pytest tests/books/test_get_book.py
```

`pytest -m unit` runs only network-independent tests. The Books and Authors tests call the public API.

## Send one API request manually

You can run one Books or Authors request without running pytest. From this project folder:

```powershell
python -m bookstore_api books list
python -m bookstore_api books get 1
python -m bookstore_api books create --data-file requests/book.json
python -m bookstore_api books update 1 --data-file requests/book.json
python -m bookstore_api books delete 1
python -m bookstore_api authors get 1
```

For create or update, pass a JSON file with `--data-file` or provide JSON directly with `--data`:

```powershell
python -m bookstore_api books create --data '{"id":9001,"title":"Example book","pageCount":120}'
```

The command prints the HTTP status and response body. It returns a nonzero exit code for HTTP errors or request failures. It sends exactly one operation per invocation; it does not run test assertions. Like the test suite, it targets the public FakeRestAPI by default and can use `BASE_URL` and `API_TIMEOUT_SECONDS` environment variables. The sample API does not persist create, update, or delete operations.

Point the suite at another host with the same routes:

```powershell
$env:BASE_URL = "https://fakerestapi.azurewebsites.net"
$env:API_TIMEOUT_SECONDS = "30"
pytest
```

## Reports

Every `pytest` run writes:

- `reports/report.html` — one row per test, with pass or fail, duration, and the log line for each call
- `reports/junit.xml` — JUnit XML for CI tools

Open `reports/report.html` in a browser. The copy in this folder is from the last local run.

## Project structure

```text
bookstore-api-tests/
├── bookstore_api/
│   ├── config.py         Base URL and timeout
│   ├── cli.py            Run one API request from the command line
│   ├── http_client.py    HTTP transport, logging, safe-read retry
│   ├── __main__.py       Enables python -m bookstore_api
│   ├── resources.py      Books and Authors CRUD
│   └── payloads.py       Loads JSON bodies and applies test values
├── requests/
│   ├── book.json         Synthetic book body
│   └── author.json       Synthetic author body
├── tests/
│   ├── books/            Books happy paths and edge cases
│   ├── authors/          Authors happy paths and edge cases
│   ├── unit/             Client retry behavior, no network
│   ├── assertions.py     Shared response checks
│   └── conftest.py       Pytest fixtures
├── reports/              HTML and JUnit output
└── .github/workflows/    GitHub Actions pipeline
```

## Design

Each module has one job.

- `HttpClient` only sends requests. It logs the method, URL, status code, and a short response snippet. It retries safe `GET`, `HEAD`, and `OPTIONS` requests once on HTTP 5xx, a timeout, or a connection error. It does not retry write requests or 4xx responses, avoiding accidental repeated side effects when a write's outcome is uncertain.
- `ResourceApi` knows the collection path. `BooksApi` and `AuthorsApi` are that class with the collection name fixed, so a new collection does not require a new HTTP stack.
- Request bodies live in `requests/`. Tests pass a context of field overrides through `book_payload()` and `author_payload()` instead of building JSON inline.
- Tests receive `books_api` or `authors_api` from fixtures. They arrange data, call one operation, and assert the status and body.
- Shared checks for problem responses and object shape live in `tests/assertions.py`.

## What this demo API does

FakeRestAPI stores a fixed catalog. `POST`, `PUT`, and `DELETE` return success and echo the body you sent, then leave the catalog unchanged. The tests lock that behavior in:

- A created book or author with id `9001` is not returned by a later GET.
- Updating or deleting book `1` or author `1` does not change the stored title or name. Each book response stamps a new `publishDate`, so that field is not compared across calls.
- An empty JSON object is accepted and comes back with default values (`id` 0, null text fields).
- A missing numeric id is `404` on GET. The same missing id is `200` on PUT and DELETE.
- A non-numeric id such as `abc` is `400` for GET, PUT, and DELETE.
- A book body with the wrong JSON types, or a body that is not JSON, is `400`.

Author names in `requests/author.json` are the synthetic values `Fake` and `Person`. Book text is a fabricated catalog entry.

## CI

`.github/workflows/api-tests.yml` runs Ruff and the network-independent unit tests in one job, and the live Books and Authors API tests in a separate job. It uploads test reports as build artifacts and runs on push to `main` or `master`, on pull requests, and when started by hand.

## Assumptions

- The host is FakeRestAPI and the routes stay `/api/v1/Books` and `/api/v1/Authors`.
- The book catalog stays at 200 items, with book `1` titled `Book 1` and book `200` titled `Book 200`.
- Author `1` stays `First Name 1` / `Last Name 1` on book `1`.
- Success for create and update is HTTP 200, which is what this API documents, rather than 201 or 204.
- The Books and Authors tests need a network path to the public API; an outage can fail those tests. The unit tests do not call the network and can run independently with `pytest -m unit`.
