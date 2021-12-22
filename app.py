from flask import Flask
from flask import request
import pymongo
import requests

app = Flask(__name__)

service_name = "database_core_service"
service_ip = "34.159.211.186:5000"

ecostreet_core_service = "34.120.106.247"
configuration_core_service = "192.168.1.121"

users = [{"username":"admin", "password":"admin", "AccessToken":"0x7ac93hd98s"},{"username":"matej", "password": "1337h4x0r", "AccessToken":"0xf8423ab29c"}]

@app.route("/")
def hello_world():
    return "Database microservice."
    
@app.route('/authenticate', methods = ['POST'])
def login():
    global ecostreet_core_service
    global configuration_core_service
    try:
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
    
@app.route("/update_ip")
def update_ip():
    global ecostreet_core_service
    global configuration_core_service
    data = {"name": service_name, "ip": service_ip}
    url = 'http://' + configuration_core_service + '/update'
    response = requests.post(url, data=data)
    return response.text

@app.route("/config", methods = ['POST'])
def config_update():
    global ecostreet_core_service
    global configuration_core_service
    try:
        microservice = request.form["name"]
        ms_ip = request.form["ip"]
        if microservice == "database_core_service":
            ecostreet_core_service = ms_ip
        if microservice == "configuration_core_service":
            configuration_core_service = ms_ip
        return "200 OK"
    except Exception as err:
        return err

@app.route("/getconfig")
def get_config():
    global ecostreet_core_service
    global configuration_core_service
    return str([ecostreet_core_service, configuration_core_service])

