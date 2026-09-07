Graduation the celebrate market certificate by post postmaster cotron# Call-E Municipal Intelligence Platform

This guide explains how to configure, run, call, analyze, and troubleshoot the platform.

## What the platform does

The platform has four runtime parts:

1. **Call-E agent** receives a citizen phone call, asks for the incident details, validates the location through the MCP server, and sends the completed call to the webhook.
2. **FastAPI service** receives the Call-E webhook, stores the call in SQLite, and schedules language-model analysis.
3. **Analysis pipeline** generates summaries, sentiment, topics, embeddings, clusters, and policy insights.
4. **Streamlit dashboard** displays call volume, issue distribution, sentiment, recent calls, clusters, and insights.

The supported demo locations are defined in `app/services/mcp_server.py`.

## Requirements

Install:

- Python 3.10 or newer
- A Call-E account and API key
- A Gemini API key for summaries, sentiment, topics, embeddings, and insights
- `ngrok` or another public HTTPS tunnel for Call-E callbacks and MCP access
- The Call-E Python SDK that provides `from calle import CalleClient`

The Call-E SDK is account-specific and is intentionally not pinned in `requirements.txt` because the package is not available from the configured public package index. Install it using the package name and command supplied by Call-E.

## Install the project

From the repository directory:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks virtual-environment activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

The dashboard uses native `pyarrow.Table` values for charts and tables. This avoids the pandas-to-Arrow conversion failure that occurs with incompatible pandas/pyarrow installations.

## Configure `.env`

Copy the example file and edit the values:

```powershell
Copy-Item .env.example .env
```

Required values:

```dotenv
DATABASE_URL=sqlite:///./city_incidents.db
CALLE_API_KEY=your_calle_api_key
CALLE_PHONE_NUMBER=+1234567890
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash
GEMINI_EMBEDDING_MODEL=models/embedding-001
MCP_SERVER_URL=https://your-public-mcp-host.example/sse
WEBHOOK_URL=https://your-public-api-host.example/webhook/call-e
```

For local-only testing, `MCP_SERVER_URL=http://localhost:8001/sse` is sufficient. A real Call-E agent needs a public HTTPS MCP URL and a public HTTPS webhook URL.

Never commit `.env`. If a real credential was ever committed or shared, rotate it before using the project.

## Initialize and seed the database

The API initializes the tables on startup. To add three local demo calls:

```powershell
python scripts/populate_db.py
```

The seed script uses stable `manual_...` call IDs. If it is run again after the records already exist, SQLite will reject duplicate IDs; delete the local `city_incidents.db` first if you want a fresh demo database.

## Start the API

Use a separate terminal with the virtual environment active:

```powershell
uvicorn app.main:app --reload --port 8000
```

Check the service:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","service":"municipal-intelligence"}
```

The Call-E webhook endpoint is:

```text
POST http://127.0.0.1:8000/webhook/call-e
```

## Start the MCP location server

In another terminal:

```powershell
python -m app.services.mcp_server
```

It listens on port `8001` using SSE. Expose it publicly for Call-E:

```powershell
ngrok http 8001
```

Set the resulting HTTPS URL plus `/sse` as `MCP_SERVER_URL` in `.env`.

Location behavior:

- Known city and street: `VALID_LOCATION`
- Unknown city: `INVALID_CITY`
- Very short unknown street: `AMBIGUOUS_STREET`
- Longer unknown street: `INVALID_STREET`

Direct local check:

```powershell
python -c "from app.services.mcp_server import verify_location; print(verify_location('Springfield', 'Main St')); print(verify_location('Unknown City', 'Main St')); print(verify_location('Springfield', 'Unknown Road'))"
```

## Expose the API webhook

In a separate terminal, expose port `8000`:

```powershell
ngrok http 8000
```

Set the HTTPS forwarding URL plus `/webhook/call-e` as `WEBHOOK_URL` in `.env`.

Use separate tunnels for the MCP server and API, or use another public reverse proxy that routes both services correctly.

## Configure and attach the Call-E agent

After both public URLs are configured and reachable:

```powershell
python scripts/configure_agent.py
```

The script creates the Municipal Incident Dispatcher and attaches it to `CALLE_PHONE_NUMBER`.

The agent workflow is:

1. Ask what issue the citizen is reporting.
2. Ask for the city and street address or landmark.
3. Call `verify_location` immediately.
4. Clarify invalid or incomplete locations.
5. Collect issue type and severity.
6. Finish with the structured fields `city`, `location`, `issue_type`, and `severity`.
7. Send the completed call to the webhook.

## Make a real call

Call the configured Call-E number and report an incident such as:

```text
There is a high-severity pothole on Main St in Springfield.
```

Confirm that the agent asks for missing information and validates the location. The webhook stores the result using `call_id` as an idempotency key, so repeated delivery of the same Call-E event does not create a duplicate record.

## Test the webhook without a phone call

With the API running, send a representative payload:

```powershell
$payload = @{
    call_id = "test-call-001"
    transcript = "There is a pothole on Main St in Springfield. It is blocking traffic."
    structured_result = @{
        city = "Springfield"
        location = "Main St"
        issue_type = "pothole"
        severity = "high"
    }
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/webhook/call-e `
    -Method Post `
    -ContentType "application/json" `
    -Body $payload
```

Expected first response:

```json
{"status":"stored","id":1}
```

Sending the same payload again returns `already_stored` instead of creating a duplicate.

## Run analysis

The webhook automatically schedules summary, sentiment, and topic analysis. That work requires a valid `GEMINI_API_KEY`.

To run the complete batch pipeline manually:

```powershell
python scripts/run_analysis.py
```

The batch pipeline performs these steps:

1. Generate or update Gemini embeddings for every call.
2. Cluster available embeddings with KMeans.
3. Generate one actionable insight per cluster.

The pipeline skips clustering when fewer than two embeddings exist and checks that embedding dimensions are consistent.

## Start the dashboard

In another terminal:

```powershell
streamlit run dashboard/streamlit_app.py
```

Open:

```text
http://localhost:8501
```

The dashboard reads the same SQLite database and displays:

- Daily call volume
- Issue distribution
- Sentiment breakdown
- The ten most recent calls
- Incident clusters
- Generated policy insights

The dashboard deliberately uses native Arrow tables rather than pandas dataframes for all Streamlit display boundaries. This avoids errors such as `StreamlitDataframeConversionError` and `ArrowTypeError` from the installed pandas/pyarrow combination.

## Complete local demo order

Use these terminals:

**Terminal 1: API**

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: sample data or webhook test**

```powershell
.\venv\Scripts\Activate.ps1
python scripts/populate_db.py
```

**Terminal 3: analysis**

```powershell
.\venv\Scripts\Activate.ps1
python scripts/run_analysis.py
```

**Terminal 4: dashboard**

```powershell
.\venv\Scripts\Activate.ps1
streamlit run dashboard/streamlit_app.py
```

For a real Call-E call, replace the seed step with the MCP tunnel, API tunnel, agent configuration, and phone call steps above.

## Verification checks

Compile every source file:

```powershell
python -m compileall app dashboard scripts
```

Check the location tool:

```powershell
python -c "from app.services.mcp_server import verify_location; assert verify_location('Springfield', 'Main St').startswith('VALID_LOCATION'); assert verify_location('Unknown City', 'Main St').startswith('INVALID_CITY'); assert verify_location('Springfield', 'Unknown Road').startswith('INVALID_STREET'); print('location checks passed')"
```

Check the API health endpoint:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Troubleshooting

### Arrow or dataframe conversion errors

Stop the dashboard, activate the project virtual environment, and reinstall requirements:

```powershell
python -m pip install --upgrade --force-reinstall -r requirements.txt
```

Restart Streamlit. The dashboard should use `pyarrow.Table` objects and should not pass `Counter` or pandas dataframes into chart functions.

### `ModuleNotFoundError: calle`

Install the Call-E SDK from the official Call-E distribution or configure that SDK's package index. The public requirements file cannot install a package that is unavailable from the configured index.

### Analysis produces no summary or insight

Check `GEMINI_API_KEY`, then inspect the API terminal for analysis errors. Embeddings and insights require Gemini access; the dashboard can still show stored calls without them.

### Database appears empty

Make sure API, scripts, and Streamlit are started from the repository or use the absolute default database path created by `app/config.py`. Check that all processes use the same `.env` and database file.

### Agent cannot reach MCP or webhook

Confirm both URLs are HTTPS, publicly reachable, current tunnel URLs, and include the correct suffixes:

- MCP: `/sse`
- Webhook: `/webhook/call-e`

## Operational notes

- The local database is SQLite and is not intended for concurrent production writes.
- The example location list is not an authoritative municipal address database.
- The Call-E API integration depends on the SDK and account permissions.
- Rotate API keys immediately if they are exposed.
