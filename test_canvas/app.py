# import requests
# from flask import Flask, jsonify, render_template, request

# app = Flask(__name__)

# servers = []

# cliendIDs = {}

# @app.route('/registerClient/<clientID>', methods=["PUT"])
# def PUT_registerClient(clientID):
    
#     # this puts a json with the following
#     # token : auth token for the server
#     # url : "http://server:port/"
#     # author : "Your Name"

#     author = "Rohan"
#     url = "http://127.0.0.1:34000/"

#     # if clientID is in use return 415 "ClientID already exists"

#     # post json with microservice ip and port

#     # otherwise return 200 "success" and json with
#     # xdim : int // in tiles
#     # ydim : int // in tiles
#     # tilesize : int

#     if clientID in cliendIDs:
#         return jsonify({"error": "ClientID already exists"}), 415
    
#     data = []

#     try:
#         data = request.get_json()
#     except:
#         return jsonify({"error": "Malformed JSON"}), 400
    
#     author = data.get("author")
#     url = data.get("url")
#     token = data.get("token")

#     if not author or not url or not token:
#         return jsonify({"error": "Malformed JSON"}), 400
    
#     cliendIDs[clientID] = {"author": author, "url": url, "token": token}

#     # Return success and canvas information
#     return jsonify({"xdim": 10, "ydim": 10, "tilesize": 5}), 200

   

# @app.route('/registerImage/<clientID>', methods=["POST"])
# def POST_registerImage(clientID):
#     # post png image of correct size

#     # 500 "Image size invalid" if image does not match required size
#     # 416 "ClientID not registered" if client was not registered
    
#     # otherwise return 200 "success"

#     if clientID not in cliendIDs:
#         return jsonify({"error": "ClientID not registered"}), 416
    
#     if not validate_image_size(request.data):
#         return jsonify({"error": "Image size invalid"}), 500
    
#     # Save image to disk
#     with open("images/" + clientID + ".png", "wb") as f:
#         f.write(request.data)

#     return jsonify({"success": "Image registered"}), 200
    

import json
import logging
from flask import Flask, jsonify, send_file, render_template, request
import requests
import base64
import dotenv

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/all')
def all():
    return render_template('all.html')

def init():
    dotenv.load_dotenv()

status = 'accept'
xdim = 10
ydim = 10
tilesize = 5
xloc = 0
yloc = 0
voteToken = '45046605-4ef3-4dfc-84ed-cfafade8a2db'
# For simple testing just use one client
approved = 'true'
currentAuthToken = 'none'
currentClientID = 'none'
currentURL = 'none'
currentAuthor = 'none'

@app.route('/getState', methods=['GET'])
def GET_state():
    state = jsonify({
        'status':status,
        'xdim':xdim,
        'ydim':ydim,
        'tilesize':tilesize,
        'xloc':xloc,
        'yloc':yloc,
        'voteToken':voteToken,
        'approved':approved,
        'currentAuthToken':currentAuthToken,
        'currentAuthor':currentAuthor,
        'currentClientID':currentClientID,
        'currentURL':currentURL
    })
    return state, 200

@app.route('/accept', methods=['POST'])
def POST_accept():
    global status
    status = 'accept'
    return "OK", 200

@app.route('/reject', methods=['POST'])
def POST_reject():
    global status
    status = 'reject'
    return "OK", 200

@app.route('/registerImage/<clientID>', methods=["POST"])
def POST_registerImage(clientID):
    global status
    if (status == 'accept'):
        return "OK", 200
    else:
        return "Wrong Dimension", 500

@app.route('/registerClient/<clientID>', methods=["PUT"])
def PUT_registerClient(clientID):
    # this puts a json with the following
    # token : auth token for the server
    # url : "http://server:port/"
    # author : "Your Name"
    data = request.json
    print("registerClient/", clientID, json.dumps(data))

    global currentClientID
    currentClientID = clientID
    global currentURL
    currentURL = data["url"]
    global currentAuthToken
    currentAuthToken = data["token"]
    global currentAuthor
    currentAuthor = data["author"]
    
    # otherwise return 200 "success" and json with
    # xdim : int // in tiles
    # ydim : int // in tiles
    # tilesize : int
    canvasInfo = jsonify({
        'xdim':xdim,
        'ydim':ydim,
        'tilesize':tilesize
    })
    return canvasInfo, 200

@app.route("/registeredTest", methods=["GET"])
def GET_registeredTest():

    state = jsonify({
        'xloc':xloc,
        'yloc':yloc,
        'voteToken':voteToken,
        'approved':approved,
        'currentAuthToken':currentAuthToken,
    })

    response = requests.put(f'{currentURL}/registered', data=json.dumps(state), headers={'Content-Type': 'application/json'})

    return response