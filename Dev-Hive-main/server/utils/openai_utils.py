from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_embedding(text):
    res = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return res.data[0].embedding
