import requests

from lib.api_key import get_api_key


def send_task(task_name, answer, url="https://centrala.ag3nts.org/report"):
    data = {
        "task": task_name,
        "apikey": get_api_key(),
        "answer": answer
    }
    print(data)

    post_response = requests.post(url, json=data)

    if post_response.status_code == 200:
        print("POST request successful")
        print("Response:", post_response.json())  # Assuming the response is in JSON format
        code = post_response.json()['code']
        message = post_response.json()['message']
        print(f"Code: {code}")
        print(f"Message: {message}")
        return message
    else:
        print(f"Failed to send POST request. Status code: {post_response.status_code}")
        print(post_response.content)
