import requests
from flask import Flask, jsonify, render_template, request, send_file, url_for, redirect
from PIL import Image
from time import sleep

app = Flask(__name__)

neighbors = []

is_approved = False
vote_token = ""
x_loc = 0 
y_loc = 0
my_auth_token = "2514c11e-8e40-11ee-b9d1-0242ac120002"

# image_data = {
#     "authToken": my_auth_token,
#     "xloc": x_loc,
#     "yloc": y_loc
# }

vote_approved = False
vote_data = {}

full_image = ""
cropped_image = ""
my_tile = ""

vote_info = {
    "authToken": my_auth_token,
    "votes": 0,
    "seq": 0
}

register = {
    "author": "Rohan Gudipaty",
    # "url": "http://127.0.0.1:34000/",
    "url": "http://fa23-cs340-080.cs.illinois.edu:5001",
    "token": my_auth_token
}

xdim = 0
ydim =  0
tilesize = 0

############################################################################################################################################       

# response_client = requests.put("http://127.0.0.1:5000/registerClient/rohanvg3", json=register)
response_client = requests.put("http://fa23-cs340-adm.cs.illinois.edu:34000/registerClient/rohanvg3", json=register)


# Check the status code of the response
if response_client.status_code == 200:
    print("Client registration successful!\n")
    canvas_response = response_client.json()
    xdim = canvas_response["xdim"]
    ydim = canvas_response["ydim"]
    tilesize = canvas_response["tilesize"]
elif response_client.status_code == 400:
    print("Bad Request: JSON is malformed.")
elif response_client.status_code == 415:
    print("Unsupported Media Type: ClientID is already registered.")
else:
    print(f"Unexpected response: {response_client.status_code}")
    print(response_client.text)

############################################################################################################################################       

def make_tile(im):
    global x_loc, y_loc, tilesize, my_tile
    current_im = Image.open(im)
    left = x_loc * tilesize
    right = (x_loc + 1) * tilesize
    top = y_loc * tilesize
    bottom = (y_loc + 1) * tilesize
    resized_im = current_im.crop((left, top, right, bottom))
    my_tile = f"current_tile.png"
    resized_im.save(my_tile)

@app.route('/')
def init():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global full_image, cropped_image

    if request.method == 'POST':

        uploaded_image = request.files['image']

        if uploaded_image:
            # Save the uploaded image
            full_image = uploaded_image.filename
            print("Saving image line 103: ", full_image)
            uploaded_image.save(full_image)
            print("Image saved line 105: ", full_image)
        
            original_image = Image.open(full_image)
            print("Image opened line 108: ", full_image)
            resized_image = original_image.resize((xdim * tilesize, ydim * tilesize))
            print("Image resized line 110: ", full_image)
            cropped_image = f"current_resized.png"
            resized_image.save(cropped_image)


            file = {"file": open(cropped_image, "rb")}
            response_image = requests.post("http://fa23-cs340-adm.cs.illinois.edu:34000/registerImage/rohanvg3", files=file)
            sleep(2)
            print(response_image.content)

            if response_image.status_code == 200:
                print("Image registration successful!\n")
            elif response_image.status_code == 416:
                print("ClientID not registered.")
            elif response_image.status_code == 500:
                print("Image size invalid.")
            else:
                print(f"Unexpected response: {response_image.status_code}")
                print(response_image.text)

            return redirect('/checkImageStatus')

    return render_template('upload.html'), 200


@app.route('/checkImageStatus', methods=["GET"])
def get_image_status():
    global is_approved
    if is_approved == True:
        return redirect('/success_image')
    else:
        return redirect('/upload')

@app.route('/success_image')
def success():
    # global image_data
    global cropped_image, x_loc, y_loc, my_auth_token, my_tile
    return render_template('success_image.html', image_path=cropped_image, authToken=my_auth_token, x_loc=x_loc, y_loc=y_loc)


@app.route('/registered', methods=["PUT"])
def PUT_registered():

    print("REDIRECTED")
    global is_approved, vote_token, x_loc, y_loc
    global tilesize, my_tile
    global full_image, cropped_image
    data = []

    try:
        data = request.get_json()
    except:
        print("Malformed JSON")
        return jsonify({"error": "Malformed JSON"}), 400
    

    auth_token = data.get("authToken")
    # is_approved = data.get("approved")
    vote_token = data.get("voteToken")
    x_loc = data.get("xloc")
    y_loc = data.get("yloc")

    print("OLD DATA\n")

    print("auth_token: ", auth_token)
    # print("is_approved: ", is_approved)
    print("vote_token: ", vote_token)
    print("x_loc: ", x_loc)
    print("y_loc: ", y_loc)

    if auth_token != my_auth_token:
        print("Authorization token invalid")
        return jsonify({"error": "Authorization token invalid"}), 455

    if data.get("approved") == True or data.get("approved") == "True" or data.get("approved") == "true":
        is_approved = True
        print("Approved!\n")
        print("full_image: ", full_image)
        print("cropped_image: ", cropped_image)
        
        make_tile(cropped_image)

    else:
        print("Not approved!\n")

    return "success", 200

    
############################################################################################################################################       


@app.route('/image', methods=["GET"])
def get_full_image():
    global is_approved, cropped_image
    if is_approved == True:
        return send_file(cropped_image)
    else:
        return jsonify({"error": "Image not approved"}), 404

@app.route('/tile', methods=["GET"])
def get_tile_image():
    #WRONG
    global is_approved, my_tile
    if is_approved == True:
        return send_file(my_tile)
    else:
        return jsonify({"error": "Image not approved"}), 404

@app.route('/votes', methods=["GET"])
def get_votes():
    global vote_info
    return_json = {
        "votes": vote_info["votes"],
    }
    return return_json, 200

@app.route('/votes', methods=["PUT"])
def put_votes():
    global vote_info

    global my_auth_token

    # global my_auth_token, votes_count, seq_number

    data = []

    try:
        data = request.get_json()
    except:
        print("Malformed JSON")
        return jsonify({"error": "Malformed JSON"}), 400

    if data.get('authToken') != my_auth_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    if data.get('seq') < vote_info["seq"]:
        return jsonify({"error": "Conflict"}), 409
    
    vote_info["votes"] = data.get("votes")
    vote_info["seq"] = data.get("seq")

    return "success", 200

############################################################################################################################################       

@app.route('/castVote', methods=["GET", "POST"])
def cast_vote():

    global vote_info, vote_token
    
    global vote_approved, vote_data

    if request.method == 'POST':

        # Retrieve data from the form
        x = int(request.form.get("x_loc"))
        y = int(request.form.get("y_loc"))

        vote_data = {
            "voteToken": vote_token,
            "xloc": x,
            "yloc": y
        }

        # cast_vote_response = requests.put(f"http://127.0.0.1:5000/vote/rohanvg3", json=vote_data)

        print("line 340")

        cast_vote_response = requests.put(f"http://fa23-cs340-adm.cs.illinois.edu:34000/vote/rohanvg3", json=vote_data)

        if cast_vote_response.status_code == 200:
            vote_approved = True
            print("PUT request successful!")
        #     return render_template('success_vote.html', vote_data=vote_data)
        # else:
        #     return redirect('/castVote')

        
        return redirect('/checkVoteStatus')

    return render_template('castVote.html')

@app.route('/checkVoteStatus', methods=["GET"])
def get_vote_status():
    global vote_approved, vote_data
    if vote_approved == True:
        return redirect('/success_vote')
    else:
        return redirect('/castVote')

       
@app.route('/success_vote')
def success_vote():
    global vote_data
    curr_votes = requests.get(f"http://fa23-cs340-080.cs.illinois.edu:5001/votes").json()
    return render_template('success_vote.html', vote_data=vote_data, numVotes = curr_votes["votes"])

############################################################################################################################################

@app.route('/update', methods=["PUT"])
def update():

    global my_auth_token, neighbors

    data = []

    try:
        data = request.get_json()
    except:
        print("Malformed JSON")
        return jsonify({"error": "Malformed JSON"}), 400
    
    if data.get("authToken") != my_auth_token:
        return jsonify({"error": "Unauthorized"}), 401
    
    # ####
    # if data.get('seq') < vote_info["seq"]:
    #     return jsonify({"error": "Conflict"}), 409
    
    # vote_info["votes"] = data.get("votes")
    # vote_info["seq"] = data.get("seq")
    # ####

    max_votes = vote_info["votes"]
    max_neighbor = None
    
    neighbors = data.get("neighbors")

    for neighbor in neighbors:
        url = f"{neighbor}/votes"
        info = {}
        try:
            info = requests.get(url).json()
        except:
            print("Malformed neighbor JSON")
            return jsonify({"error": "Malformed neighbor JSON"}), 400
        if info["votes"] > max_votes:
            max_votes = info["votes"]
            max_neighbor = neighbor

    
    if max_neighbor != None:
        url = f"{max_neighbor}/image"
        neighbor_image = None
        try:
            neighbor_image = requests.get(url)
        except:
            print("Malformed neighbor JSON")
            return jsonify({"error": "Malformed neighbor JSON"}), 400
        
        with open(cropped_image, "wb") as f:
            f.write(neighbor_image.content)
        print("Image updated")

        make_tile(cropped_image)
        print("Tile updated")

        return f"this neighbor has max votes: {max_neighbor}", 200
    
    return "my image has most votes", 200

############################################################################################################################################

@app.route('/dashboard')
def dash():
    global my_auth_token, x_loc, y_loc, cropped_image, my_tile,  xdim, ydim, tilesize, vote_data
    curr_votes = requests.get(f"http://fa23-cs340-080.cs.illinois.edu:5001/votes").json()
    return render_template('dashboard.html', authToken=my_auth_token, x_loc=x_loc, y_loc=y_loc, vote_data=vote_data, xdim=xdim, ydim=ydim, tilesize=tilesize, numVotes = curr_votes["votes"])