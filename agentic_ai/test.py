# test_model.py
from config import client, MODEL_NAME

response = client.models.generate_content(
    model=MODEL_NAME,
    contents="Say 'API is working' if you can read this."
)

print(response.text.strip())