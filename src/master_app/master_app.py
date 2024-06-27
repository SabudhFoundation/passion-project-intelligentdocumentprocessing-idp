import logging
from flask import Flask, render_template, send_from_directory, redirect

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='master_app.log', level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico')

@app.route('/summarization')
def summarization():
    return redirect("http://localhost:8083", code=302)

@app.route('/table_extraction')
def table_extraction():
    return redirect("http://localhost:8080", code=302)

@app.route('/ner')
def ner():
    return redirect("http://localhost:8081", code=302)

@app.route('/about')
def about():
    return redirect("http://localhost:8086", code=302)


@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("An error occurred: %s", e)
    return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8085)
