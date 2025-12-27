Transaction Webhook API
=======================

This project implements a cloud-deployed webhook service that accepts transaction
events, responds immediately, and processes them asynchronously while ensuring
idempotency and persistent storage.

The backend is built using FastAPI, deployed on Render, and uses Supabase
PostgreSQL as a cloud-based database.

--------------------------------------------------
LIVE DEPLOYMENT
--------------------------------------------------

Backend Base URL:
https://transactionwebhookapi-s.onrender.com/

Swagger UI:
https://transactionwebhookapi-s.onrender.com/docs

--------------------------------------------------
SYSTEM OVERVIEW
--------------------------------------------------

Key characteristics:

- Responds to webhook requests with HTTP 202 Accepted
- Response time under 500ms
- Asynchronous background processing
- Simulated processing delay of approximately 30 seconds
- Idempotent handling using transaction_id
- Persistent cloud storage
- Publicly accessible cloud deployment

--------------------------------------------------
ARCHITECTURE
--------------------------------------------------

Client / Webhook Sender
        |
        v
FastAPI Service (Render)
- Immediate 202 response
- Background task execution
        |
        v
Supabase PostgreSQL
- Persistent transaction storage

--------------------------------------------------
TECH STACK
--------------------------------------------------

- Framework: FastAPI
- ORM: SQLAlchemy
- Database: Supabase PostgreSQL
- Connection: PgBouncer pooler
- Deployment: Render
- Server: Uvicorn

--------------------------------------------------
ENVIRONMENT VARIABLES
--------------------------------------------------

Required environment variable:

DATABASE_URL
postgresql://postgres.<project-ref>:<password>@aws-<region>.pooler.supabase.com:6543/postgres

Notes:
- Password must be URL-encoded
- Pooler endpoint is required for cloud compatibility
- Environment variables are not committed to the repository

--------------------------------------------------
RUNNING THE APPLICATION
--------------------------------------------------

Recommended:
Use the deployed Render service.

Optional local run:

1. Create virtual environment
   python -m venv venv

2. Activate virtual environment
   Windows: venv\Scripts\activate
   Mac/Linux: source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Run the server
   uvicorn app.main:app --reload

Note:
Local environments may have DNS or network restrictions when connecting
to Supabase.

--------------------------------------------------
API ENDPOINTS
--------------------------------------------------

1) Health Check

GET /health

Response:
{
  "status": "healthy"
}

--------------------------------------------------

2) Transaction Webhook

POST /v1/webhooks/transactions

Description:
Accepts a transaction event and immediately acknowledges receipt.
Processing occurs asynchronously.

(Demo)Request Body:
{
  "transaction_id": "txn_001",
  "source_account": "US",
  "destination_account": "India",
  "amount": 100,
  "currency": "USD"
}

Response:
HTTP 202 Accepted

--------------------------------------------------

3) Fetch Transaction Status

GET /v1/transactions/{transaction_id}

(Demo)Response:
{
  "transaction_id": "txn_001",
  "status": "PROCESSED",
  "created_at": "2025-01-01T10:00:00Z",
  "processed_at": "2025-01-01T10:00:30Z"
}

--------------------------------------------------
BACKGROUND PROCESSING
--------------------------------------------------

- Incoming transactions are stored with status PENDING
- A background task waits approximately 30 seconds
- Status is updated to PROCESSED
- processed_at timestamp is recorded

This ensures:
- Fast API responses
- Non-blocking request handling
- Reliable transaction processing

--------------------------------------------------
IDEMPOTENCY
--------------------------------------------------

- transaction_id is enforced as a unique identifier
- Duplicate webhook requests with the same transaction_id:
  - Do not create duplicate records
  - Do not re-trigger processing
  - Still return HTTP 202 Accepted

--------------------------------------------------
DATABASE SCHEMA
--------------------------------------------------

transactions table:

- transaction_id (primary key)
- source_account
- destination_account
- amount
- currency
- status
- created_at
- processed_at

--------------------------------------------------
ASSESSMENT REQUIREMENTS COVERED
--------------------------------------------------

- HTTP 202 Accepted response
- Response time under 500ms
- Asynchronous background processing
- Simulated 30-second delay
- Idempotent webhook handling
- Persistent cloud storage
- Cloud deployment
- Public API endpoint

--------------------------------------------------
AUTHOR
--------------------------------------------------

Subhojit Ganguly
Full Stack Developer

GitHub:
https://github.com/<your-username>
