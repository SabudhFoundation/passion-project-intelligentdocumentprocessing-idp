import logging
from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='about_app.log', level=logging.DEBUG)

@app.route('/')
def index():
    return render_template('about.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(Exception)
def handle_exception(e):
    logging.exception("An error occurred: %s", e)
    return "Internal Server Error", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8086)
