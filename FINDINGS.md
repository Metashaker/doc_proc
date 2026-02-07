# FINDINGS

## Security

### SQL injection in search endpoint
- **What:** The search route builds SQL with string interpolation in `backend/app/routes/search.py`.
- **Why it matters:** User input can alter the query, exposing or damaging data.
- **How we fixed it:** Use parameterized queries (or SQLAlchemy query builder) and add a regression test; add `pg_trgm` index for performance.

### Path traversal on upload
- **What:** Upload uses `file.filename` directly to build a file path in `backend/app/routes/documents.py`.
- **Why it matters:** Crafted filenames can write files outside the upload directory.
- **How we fixed it:** Sanitize filenames and store with UUIDs inside a controlled upload directory; keep original filename in DB.

### Hardcoded secrets and credentials
- **What:** `backend/app/config.py` contains a hardcoded `SECRET_KEY` and a default DB password.
- **Why it matters:** Secrets in code can leak and are unsafe for production.
- **How we fixed it:** Load secrets from environment variables; fail fast if missing in non-dev.

### Overly permissive CORS
- **What:** `allow_origins=["*"]` and `allow_credentials=True` in `backend/app/main.py`.
- **Why it matters:** Allows credentialed requests from any origin.
- **How we fixed it:** Read allowed origins from an environment variable and disable credentials unless required.

### Unvalidated file uploads
- **What:** No file type, size, or content validation for uploads.
- **Why it matters:** Enables storage of unexpected files and potential DoS via large uploads.
- **How we fixed it:** Enforce PDF-only uploads with a 25 MB limit (future: allow Word docs).

### File overwrite risk on upload
- **What:** Uploaded file is saved using the original filename with no collision handling.
- **Why it matters:** A new upload can overwrite an existing file on disk.
- **How we fixed it:** Store files using UUID filenames and keep original name in the DB.

## Performance & Scalability

### Blocking PDF extraction inside async request
- **What:** PyMuPDF extraction runs in the request handler (`backend/app/services/pdf_processor.py`).
- **Why it matters:** CPU-bound work blocks the event loop, reducing throughput.
- **How we fixed it:** Offload extraction to `BackgroundTasks` (note: for production use Celery/RQ/Dramatiq for retries/durability).

### Full-file reads into memory
- **What:** `await file.read()` loads the entire upload into memory before writing.
- **Why it matters:** Large files can spike memory usage and slow the server.
- **How we fixed it:** Stream uploads to disk in chunks with size enforcement; keep upload inline and offload only PDF parsing to background tasks for large documents.

### N+1 queries on document list
- **What:** `GET /documents` queries `ProcessingStatus` per document.
- **Why it matters:** Latency grows linearly with document count.
- **How we fixed it:** Use a join/eager load to fetch statuses in a single query.

### Full table scan for search
- **What:** `ILIKE '%query%'` on `content` with no index.
- **Why it matters:** Search gets slower as data grows.
- **How we fixed it:** Add `pg_trgm` GIN index for substring search (note: tsvector/Elasticsearch for production usage).

## Reliability & Bugs

### Search breaks with quotes or special characters
- **What:** Raw SQL string interpolation fails for inputs containing `'`.
- **Why it matters:** Causes 500 errors for common queries.
- **How we fixed it:** Parameterized queries handle special characters safely.

### No error handling for PDF parsing failures
- **What:** Exceptions from `fitz.open` aren’t caught.
- **Why it matters:** A malformed PDF can crash the request.
- **How we fixed it:** Add try/except around parsing and return a clear error response.

### Upload endpoint assumes PDF content
- **What:** The upload endpoint processes any file as a PDF without validation.
- **Why it matters:** Non-PDF uploads can cause processing errors and inconsistent data.
- **How we fixed it:** Validate content-type/extension before processing.

## Code Organization & Maintainability

### Business logic concentrated in routes
- **What:** File I/O, parsing, and DB writes are all inside route handlers.
- **Why it matters:** Harder to test, extend, and reuse logic.
- **How we fixed it:** Move core logic into services (DocumentService, StorageService, PdfProcessingService, SearchService) and unit test them.

### Frontend forces full-page reload after upload
- **What:** `window.location.reload()` is used in `UploadForm`.
- **Why it matters:** Resets UI state and is inefficient compared to state updates.
- **How we fixed it:** Replace reload with state refresh and component updates.

## Database Design

### No indices for common access patterns
- **What:** No explicit indexes on fields commonly queried (e.g., content, created_at).
- **Why it matters:** Query performance degrades as data grows.
- **How we fixed it:** Add indexes for search and commonly filtered/sorted fields.

### No cascade rules on delete
- **What:** Deleting a document manually deletes status records in code instead of DB constraints.
- **Why it matters:** Inconsistent data can occur if deletions happen outside app logic.
- **How we fixed it:** Add ON DELETE CASCADE or define ORM cascade behavior.

## Testing & Validation

### No automated tests
- **What:** No test suite or configs present.
- **Why it matters:** Regressions are likely during changes.
- **How we fixed it:** Add minimal backend tests for critical flows and service unit tests per PR.


## If We Had More Time

- Add soft deletes (`deleted_at`) for documents to support recovery and auditing.
- Add support for Word document uploads alongside PDFs.
- Migrate search to `tsvector` or Elasticsearch/OpenSearch for large-scale datasets.
- Move background processing to Celery/RQ/Dramatiq for retries and durability.
- Introduce Alembic migrations for safer schema evolution.
- Add in-app PDF viewer with a dedicated file-serving endpoint.
- Store files in S3/object storage instead of local disk.
- Add pagination for document list and search results.
- Add authentication and authorization.
- Add rate limiting on upload and search endpoints.
- Add audit logging for document actions.
