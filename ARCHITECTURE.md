# Architecture Overview for the RBC Parser Service

This service exposes the three Document Intelligence parsers through a FastAPI backend, an Azure API Management gateway, and a Next.js + Vercel front-end. The flow is:

`
Vercel (Next.js/React UI)
        ?
Azure API Management (public API layer + gateway)
        ?
Azure Container App running the FastAPI backend
        ?
Azure Document Intelligence (prebuilt invoice + layout models)
`

## Public API Layer (Azure API Management)
1. Create or reuse an API Management instance in the same region as your backend.
2. Define a public API that exposes /parse/invoice, /parse/rbc-credit-card, and /parse/rbc-bank-statement.
   - Each route should forward the payload to the FastAPI container app URL (e.g., https://<container>.azurecontainerapps.io/parse/...).
   - Enable CORS, configure rate limits/quotas if needed, and optionally require subscription keys for the public API.
3. Use versions/products to gate access if you expect multiple clients.
4. Record the gateway's base URL and propagate it to the front-end (NEXT_PUBLIC_API_GATEWAY).

## FastAPI Backend (Azure Container Apps)
1. Build the container via the provided Dockerfile at the repo root.
2. Push the image to Azure Container Registry or Docker Hub.
3. Deploy an Azure Container App that exposes port 8000 and points to the parser codebase.
4. Set the following environment variables for the container:
   - DOCUMENT_INTELLIGENCE_ENDPOINT
   - DOCUMENT_INTELLIGENCE_API_KEY
5. Optionally, expose a managed identity or private link if the API Management gateway is in a virtual network.
6. Ensure the container app URL is reachable by the API Management service.

## Azure Document Intelligence
1. Create a Document Intelligence resource and note the endpoint/key (can be the existing one in parsers/shared.py).
2. Assign that endpoint/key as environment variables for the FastAPI container.
3. Consider adding network restrictions or private links once production ready.

## Client Website (Next.js + React on Vercel)
1. The Next.js app lives in the web/ directory; it provides a single upload form with parser selection.
2. It POSTs the FormData to the API Management gateway using NEXT_PUBLIC_API_GATEWAY as the base URL.
3. The UI surfaces the download once the backend returns the CSV blob.
4. Deploy the site to Vercel by pointing the project root to web/ (use the “Root Directory” override). Vercel will run 
pm install/
pm run build automatically.
5. Configure Vercel environment variables (NEXT_PUBLIC_API_GATEWAY and any others you add) via the dashboard.

## Next Steps for You
- Create the Azure resources (Document Intelligence, Container App, API Management) and wire them together.
- Deploy the backend container with the Dockerfile and ensure it passes through the API Management gateway.
- Deploy the Next.js site on Vercel, configuring the gateway URL as NEXT_PUBLIC_API_GATEWAY.
- Verify end-to-end workflow by uploading PDFs and downloading CSVs from the Vercel UI.
