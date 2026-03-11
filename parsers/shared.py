import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
load_dotenv()

ENDPOINT = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]
API_KEY = os.environ["DOCUMENT_INTELLIGENCE_API_KEY"]

def get_document_client() -> DocumentIntelligenceClient:
    return DocumentIntelligenceClient(
        endpoint=ENDPOINT,
        credential=AzureKeyCredential(API_KEY)
    )
