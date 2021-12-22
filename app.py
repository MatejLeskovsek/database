from flask import Flask
from flask import request
import pymongo
import requests

app = Flask(__name__)
mongodb_username = "admin"
mongodb_password = "1337h4x0r"

users = [{"username":"admin", "password":"admin", "AccessToken":"0x7ac93hd98s"},{"username":"matej", "password": "1337h4x0r", "AccessToken":"0xf8423ab29c"}]

@app.route("/")
def hello_world():
    return "Database microservice."
    
@app.route('/authenticate', methods = ['POST'])
def login():
    # connect to mongodb and authenticate user, return token
    try:
        #client = pymongo.MongoClient("mongo") 
        #db = client.ecostreetdb
        #user = db.users.find_one({
        #    "username": request.form["username"]
        #})
        user = None
        for suser in users:
            if suser["username"] == request.form["username"]:
                user = suser
        try:
            if(user["password"] == request.form["password"]):
                return user["AccessToken"]
            else:
                return "Error 401: Unauthorized. Login  Incorrect."
        except:
            return "Error 404: User Not Found."
    except Exception as err:
        return err
    
@app.route('/config', methods = ['POST'])
def config():
    return 200

