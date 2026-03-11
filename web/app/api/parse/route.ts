import { NextRequest } from "next/server";

export async function POST(req: NextRequest) {

  const formData = await req.formData();

  const parser = formData.get("parser");

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_GATEWAY_URL}/${parser}`,
    {
      method: "POST",
      headers: {
        "Ocp-Apim-Subscription-Key": process.env.APIM_SUBSCRIPTION_KEY!,
      },
      body: formData,
    }
  );

  const blob = await response.blob();

  return new Response(blob, {
    status: response.status,
  });
}