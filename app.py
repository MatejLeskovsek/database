import datetime
from flask import Flask
from flask import request
import pymongo
import requests

app = Flask(__name__)

service_name = "database_core_service"
service_ip = "34.159.211.186:5000"

ecostreet_core_service = "34.159.194.58:5000"
configuration_core_service = "34.141.19.56:5000"

users = [{"username":"admin", "password":"admin", "AccessToken":"0x7ac93hd98s"},{"username":"matej", "password": "1337h4x0r", "AccessToken":"0xf8423ab29c"}]

# HOME PAGE
@app.route("/")
def hello_world():
    return "Database microservice."

# USER AUTHENTICATION - DATABASE MOCKUP
@app.route('/login', methods = ['POST'])
def login():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/login accessed")
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

# COMMAND AUTHENTICATION FUNCTION
@app.route("/authenticate", methods = ['POST'])
def authenticate_request():
    global users
    print("/authenticate accessed")
    for suser in users:
        if suser["AccessToken"] == request.form["AccessToken"]:
            # additional functionalities could be implemented
            return "200 OK"
    return "401 UNAUTHORIZED"

 
# SERVICE IP UPDATE FUNCTION
@app.route("/update_ip", methods = ['POST'])
def update_ip():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/update_ip accessed")
    
    service_ip = request.form["ip"]
    
    data = {"name": service_name, "ip": service_ip}
    url = 'http://' + configuration_core_service + '/update'
    response = requests.post(url, data=data)
    return response.text

# FUNCTION TO UPDATE IP'S OF OTHER SERVICES
@app.route("/config", methods = ['POST'])
def config_update():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/config accessed")
    
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

# FUNCTION TO GET CURRENT CONFIG
@app.route("/getconfig")
def get_config():
    global ecostreet_core_service
    global configuration_core_service
    global service_ip
    global service_name
    global users
    print("/getconfig accessed")
    
    return str([ecostreet_core_service, configuration_core_service])

# HEALTH CHECK
@app.route("/health")
def get_health():
    print("/health accessed")
    start = datetime.datetime.now()
    try:
        url = 'http://' + configuration_core_service + '/healthcheck'
        response = requests.get(url)
    except Exception as err:
        return "HEALTH CHECK FAIL: configuration unavailable"
    end = datetime.datetime.now()
    
    start2 = datetime.datetime.now()
    try:
        url = 'http://' + ecostreet_core_service + '/healthcheck'
        response = requests.get(url)
    except Exception as err:
        return "HEALTH CHECK FAIL: login service unavailable"
    end2 = datetime.datetime.now()
    
    delta1 = start-end
    crt = delta1.total_seconds() * 1000
    delta2 = start2-end2
    lrt = delta2.total_seconds() * 1000
    health = {"health check": "successful", "configuration response time": crt, "login response time": lrt}
    return str(health)

@app.route("/healthcheck")
def send_health():
    print("/healthcheck accessed")
    return "200 OK"
