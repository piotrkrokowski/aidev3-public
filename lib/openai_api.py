import base64
import json
import uuid

from openai import OpenAI

from .api_key import get_api_key
from .langfuse_api import get_openai_client_with_langfuse

SESSION_ID = str(uuid.uuid4())

def get_openapi_client():
    return OpenAI(api_key=get_api_key('openai-api-key.txt'))

def ask_agent(prompt=None, questions=[], use_langfuse=True, model="gpt-4o", temperature=0.1, max_tokens=100, name=None, image_paths=None, **kwargs):
    client = _init_client(use_langfuse)

    # For backward compatibility
    if not isinstance(questions, list):
        questions = [questions]

    messages = []

    _append_prompt(prompt, messages)

    _append_user_message(messages, questions, image_paths)

    print("Agent messages:", messages)
    
    response = client.chat.completions.create(
        messages=messages,
        session_id=SESSION_ID,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        name=name,
        **kwargs
    )

    answer = response.choices[0].message.content.strip()
    print("Agent response:", answer)

    return answer


def generate_image(prompt, use_langfuse=True, model="dall-e-3", size="1024x1024"):
    client = _init_client(use_langfuse)

    # TODO
    # if use_langfuse and name:
    #    client.set_trace_name(name)        

    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality="standard",  # "standard" or "hd"
    )
    image_url = response.data[0].url
    print(json.dumps(response.model_dump(), indent=2))
    return image_url

def transcribe_audio(file_path, use_langfuse=True, model="whisper-1"):
    return _init_client(use_langfuse).audio.transcriptions.create(
        model=model,
        file=open(file_path, "rb")
    ).text

def _init_client(use_langfuse):
    if use_langfuse:
        client = get_openai_client_with_langfuse()
    else:
        client = get_openapi_client()
    return client


def _append_prompt(prompt, messages):
    if prompt:
        messages.append(
            {
                "role": "system",
                "content": prompt,
            })


def _append_user_message(messages, questions, image_paths):
    user_content = []
    for question in questions:
        user_content.append(
            {
                "type": "text",
                "text": question,
            }
        )        

    if image_paths is not None:
        _append_images(image_paths, user_content)
    if len(user_content) > 0:
        messages.append({
            "role": "user",
            "content": user_content,
        })


def _append_images(image_paths, user_content):
    for image in image_paths:
        image_base64 = base64.b64encode(open(image, 'rb').read()).decode('utf-8')
        image_url = f"data:image/jpeg;base64,{image_base64}"
        user_content.append({
            "type": "image_url",
            "image_url": {
                "url": image_url,
                "detail": "high"
            },
        })
