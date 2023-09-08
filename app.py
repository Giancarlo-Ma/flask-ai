from flask import Flask, request, jsonify
import g4f
from g4f.Provider import Ails

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    # Parse JSON data from the request
    request_data = request.json

    # Extract required data from the request JSON
    model = request_data.get('model', 'gpt-3.5-turbo')
    messages = request_data.get('messages', [])

    # Perform chat completion
    response = g4f.ChatCompletion.create(
        model=model,
        provider=Ails,
        messages=messages,
        stream=True,
    )

    # Collect and return the chat response
    chat_response = ''.join(response)
    return jsonify({"response": chat_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
