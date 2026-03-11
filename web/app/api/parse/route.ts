import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  const url = new URL(req.url);
  const parser = url.searchParams.get("parser");
  if (!parser) return NextResponse.json({ error: "Parser not specified" }, { status: 400 });

  // Forward the request to the Azure API Management gateway
  const gatewayUrl = process.env.API_GATEWAY_URL!;
  const subscriptionKey = process.env.APIM_SUBSCRIPTION_KEY!; // server-side, secret

  const formData = await req.formData();

  const response = await fetch(`${gatewayUrl}/${parser}`, {
    method: "POST",
    body: formData,
    headers: {
      "Ocp-Apim-Subscription-Key": subscriptionKey,
    },
  });

  const blob = await response.arrayBuffer();
  return new Response(blob, {
    status: response.status,
    headers: {
      "Content-Type": "text/csv",
    },
  });
}