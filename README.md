WhizTeck Document Parser

A web portal for parsing PDFs (invoices, bank statements, and credit card statements) and extracting structured CSV data using Azure Document Intelligence. The stack includes:

Frontend: Next.js + React (deployed on Vercel)

Backend: FastAPI (running in Azure Container Apps)

API Gateway: Azure API Management

AI/ML: Azure Document Intelligence prebuilt models

Features

Upload PDFs and select the parser:

Invoice parser (vendor, date, total, currency)

Bank statement parser (transaction normalization)

Credit card parser (tables & foreign currency)

Optional statement year for bank or credit card statements

CSV download of parsed data

Secure handling of API keys via environment variables

Folder Structure
/parsers           # Python parser logic
/web                # Next.js frontend
  /app              # Page and component code
  /api              # Server-side API routes
  globals.css       # Styling
  package.json
  tsconfig.json
  README.md
/main.py            # FastAPI entrypoint
/Dockerfile
/architecture.md    # System architecture and deployment notes
Local Development
1. Backend (FastAPI)

Ensure your Document Intelligence environment variables are set in .env:

DOCUMENT_INTELLIGENCE_ENDPOINT=https://<your-resource>.cognitiveservices.azure.com/
DOCUMENT_INTELLIGENCE_API_KEY=<your-api-key>

Run FastAPI locally:

python -m venv .venv
source .venv/Scripts/activate   # Windows
pip install -r requirements.txt
uvicorn main:app --reload
2. Frontend (Next.js)

Create a .env.local file in /web with the following:

API_GATEWAY_URL=http://localhost:8000     # Local FastAPI backend
APIM_SUBSCRIPTION_KEY=<your-subscription-key>   # Only if API Management requires key

Install dependencies and run:

cd web
npm install
npm run dev

Open http://localhost:3000
 in your browser.

Deployment
Backend (Azure Container Apps)

Build Docker image:

docker build -t whizteck-api .

Push to Azure Container Registry:

az acr login --name <registry-name>
docker tag whizteck-api <registry-name>.azurecr.io/whizteck-api:v1
docker push <registry-name>.azurecr.io/whizteck-api:v1

Deploy as Azure Container App, exposing port 8000 and setting env vars:

DOCUMENT_INTELLIGENCE_ENDPOINT

DOCUMENT_INTELLIGENCE_API_KEY

API Gateway (Azure API Management)

Create or reuse API Management instance

Define routes:

/parse/invoice

/parse/rbc-credit-card

/parse/rbc-bank-statement

Forward requests to the container app URL

Enable CORS and optional subscription key validation

Record the API Gateway URL for frontend use

Frontend (Vercel)

Create a new Vercel project, set Root Directory to /web

Configure the following environment variables in Vercel:

API_GATEWAY_URL=<Azure API Management URL>
APIM_SUBSCRIPTION_KEY=<key, if required>

Deploy — Vercel will run:

npm install
npm run build
Security

Do not commit secrets in .env or source code

Use environment variables for all subscription keys

Frontend communicates via a server-side route (/api/parse) to avoid exposing keys in the browser

Container App and API Management handle private keys for Azure Document Intelligence

Notes

.env.local and .env are ignored in Git via .gitignore

node_modules and .next are build artifacts and should not be committed

For production, ensure your container app environment variables are correctly configured in Azure

License

MIT License — feel free to modify and use internally.
