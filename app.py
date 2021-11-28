from flask import Flask
from flask import request
import pymongo

app = Flask(__name__)
mongodb_username = "admin"
mongodb_password = "1337h4x0r"

@app.route("/")
def hello_world():
    return "Database microservice."
    
@app.route('/authenticate', methods = ['POST'])
def login():
    # connect to mongodb and authenticate user, return token
    try:
        user = {"password": "1337h4x0r", "AccessToken": "0x8948437"}
    except Exception as err:
        return err
    try:
        if(user["password"] == request.form["password"]):
            return user["AccessToken"]
        else:
            return "Error 401: Unauthorized. Login Incorrect."
    except:
        return "Error 404: User Not Found."

