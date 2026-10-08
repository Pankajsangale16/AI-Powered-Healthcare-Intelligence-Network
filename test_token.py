import os
from huggingface_hub import HfApi
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

hf_token = os.environ.get("HF_TOKEN")
if hf_token:
    api = HfApi()
    try:
        user = api.whoami(token=hf_token)
        print("HF Token verified successfully:", user.get("name", "Valid User"))
    except Exception as e:
        print(f"Error validating HF_TOKEN: {e}")
else:
    print("HF_TOKEN is not configured in .env or environment.")