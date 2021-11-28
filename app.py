from flask import Flask
from flask import request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Database microservice."
    
@app.route('/authenticate', methods = ['POST'])
def login():
    # connect to mongodb and authenticate user, return token
    return("200OK")
