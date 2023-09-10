from flask import Flask, render_template, request, Response
import g4f
from g4f.Provider import DeepAi

app = Flask(__name__)


@app.route("/chat-completion", methods=["POST"])
def stream():
    if request.method == "POST":
        try:
            data = request.get_json()
            messages = data.get("messages", [])
            print(messages)
            # Ensure that messages is a list of dictionaries with 'role' and 'content' keys
            if not all(
                isinstance(msg, dict) and "role" in msg and "content" in msg
                for msg in messages
            ):
                return "Invalid messages format", 400

            def event_stream():
                # Perform chat completion
                response = g4f.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    provider=DeepAi,
                    messages=messages,
                    stream=True,
                )
                for message in response:
                    yield "{}".format(message)
                # yield "data: {}\n\n".format("Chat completed!")

            return Response(event_stream(), mimetype="text/event-stream")
        except Exception as e:
            return f"Error processing JSON data: {str(e)}", 400
    return "This endpoint only accepts POST requests", 405


if __name__ == "__main__":
    app.run(debug=True)
