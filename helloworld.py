from flask import *# Init the server
app = Flask(__name__)
app.config['SECRET_KEY'] = 'some super secret key!'# Send HTML!
@app.route('/')
def root():
    return "Hello world!"# Actually Start the App
if __name__ == '__main__':
    """ Run the app. """
    app.run(host='0.0.0.0', port='5000', debug=True)
