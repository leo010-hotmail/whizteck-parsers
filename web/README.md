# RBC Parser UI

This Next.js app lives in web/ and targets Vercel. It expects NEXT_PUBLIC_API_GATEWAY to point to the Azure API Management base URL that fronts the FastAPI service.

## Local development

`
cd web
npm install
npm run dev
`

## Deployment (Vercel)

- Create a Vercel project and set the “Root Directory” to web.
- Define NEXT_PUBLIC_API_GATEWAY in the Vercel dashboard so the form can hit the Azure API Management gateway.
- Deploy; Vercel will run 
pm run build automatically.
