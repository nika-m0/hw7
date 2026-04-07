from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Flask!'

@app.route('/api/health')
def health():
    return '{"status": "ok"}'
