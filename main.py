from flask import Flask

app = Flask(__name__)


@app.route('/<operation>/')
def answer(operation):
    if ':' in operation:
        operation = operation.replace(':', '/')
    return str(eval(operation))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)