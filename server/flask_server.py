from flask import Flask, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

@app.route('/')
def index():
    return render_template('index.html')

def start(port):
    app.run(port=port, host='127.0.0.1')
