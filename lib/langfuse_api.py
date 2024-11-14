from langfuse.openai import openai

from lib.api_key import get_api_key

# Set keys directly on the openai module
openai.api_key = get_api_key('openai-api-key.txt')
openai.langfuse_public_key = get_api_key('langfuse-public-api-key.txt')
openai.langfuse_secret_key = get_api_key('langfuse-secret-api-key.txt')


def get_openai_client_with_langfuse():
    openai.langfuse_auth_check()
    return openai
