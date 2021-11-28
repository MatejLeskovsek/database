from flask import Flask
from flask import request
import pymongo

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Database microservice."
    
@app.route('/authenticate', methods = ['POST'])
def login():
    # connect to mongodb and authenticate user, return token
    try:
        client = pymongo.MongoClient("mongodb+srv://admin:1337h4x0r@ecostreet.hqlgz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client.ecostreetdb
        user = db.users.find_one({
            "username": request.form["username"]
        })
    except:
        return "Error 500: Unable to connect to database."
    try:
        if(user["password"] == request.form["password"]):
            return user["AccessToken"]
        else:
            return "Error 401: Unauthorized. Login Incorrect."
    except:
        return "Error 404: User Not Found."

