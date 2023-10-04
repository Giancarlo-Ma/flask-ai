from flask import Flask, render_template, request, Response
from g4f import ChatCompletion
from g4f.Provider import DeepAi
import threading
import json
import random
import string
import time
from typing import Any
import subprocess    

url = "https://flask-ai.onrender.com"
def my_function():
    # 请求主页，保持唤醒
    try:
        output = subprocess.check_output(["curl", "-m8", url])
        print("保活-请求主页-命令行执行成功，响应报文:", output)
    except subprocess.CalledProcessError as e:
        print("保活-请求主页-命令行执行错误：", e)

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

# 每隔2秒执行一次 my_function
# set_interval(my_function, 60)

app = Flask(__name__)


@app.route("/chat/completions", methods=["POST"])
def stream():
    if request.method == "POST":
        try:
            model = request.get_json().get("model", "gpt-3.5-turbo")
            stream = request.get_json().get("stream", True)
            messages = request.get_json().get("messages")

            def generate_random_ip():
                parts = []
                for i in range(4):
                    parts.append(str(random.randint(0, 255)))
                return ".".join(parts)

            response = ChatCompletion.create(model=model, stream=stream, messages=messages, provider=DeepAi, headers={'x-forwarded-for': generate_random_ip()})

            completion_id = "".join(random.choices(string.ascii_letters + string.digits, k=28))
            completion_timestamp = int(time.time())

            completion_id = "".join(random.choices(string.ascii_letters + string.digits, k=28))
            completion_timestamp = int(time.time())

            if not stream:
                return {
                    "id": f"chatcmpl-{completion_id}",
                    "object": "chat.completion",
                    "created": completion_timestamp,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": response,
                            },
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {
                        "prompt_tokens": None,
                        "completion_tokens": None,
                        "total_tokens": None,
                    },
                }
            
            print(messages)
            # Ensure that messages is a list of dictionaries with 'role' and 'content' keys
            if not all(
                isinstance(msg, dict) and "role" in msg and "content" in msg
                for msg in messages
            ):
                return "Invalid messages format", 400
            def streaming():
                for chunk in response:
                    completion_data = {
                        "id": f"chatcmpl-{completion_id}",
                        "object": "chat.completion.chunk",
                        "created": completion_timestamp,
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": chunk,
                                },
                                "finish_reason": None,
                            }
                        ],
                    }

                    content = json.dumps(completion_data, separators=(",", ":"))
                    yield f"data: {content}\n\n"
                    time.sleep(0.1)

                end_completion_data: dict[str, Any] = {
                    "id": f"chatcmpl-{completion_id}",
                    "object": "chat.completion.chunk",
                    "created": completion_timestamp,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop",
                        }
                    ],
                }
                content = json.dumps(end_completion_data, separators=(",", ":"))
                yield f"data: {content}\n\n"

            return Response(streaming(), mimetype="text/event-stream")
        except Exception as e:
            return f"Error processing JSON data: {str(e)}", 400
    return "This endpoint only accepts POST requests", 405


if __name__ == "__main__":
    app.run(debug=True)
