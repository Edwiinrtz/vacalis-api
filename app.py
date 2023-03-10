from flask import Flask, request
from pymongo import MongoClient
import qrcode
from bson import ObjectId, json_util
import time, random
from werkzeug.datastructures import ImmutableMultiDict
import os


app = Flask(__name__)
app.debug = True
client = MongoClient('localhost', 27017)
db = client.vacalis
cows = db.cows 

UPLOAD_FOLDER = './static/cows/profile_photos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ACTUAL_IMAGE_ID = ""

@app.route('/')
def index():
    allCows = list()
    
    for x in cows.find({}): 
        allCows.append(x)

    return json_util.dumps(allCows)


def exist(id):

    cow = cows.find_one({'_id':id})

    if not cow : return "cow doesn't exist", 404

    return True

@app.route("/api/addImage/", methods=['POST'])
def addImage():
    global ACTUAL_IMAGE_ID
    #requested_info = request.form()
    profile_image = request.files['image']
    profile_img_name = ACTUAL_IMAGE_ID+".jpg"
    path = (os.path.join(app.config['UPLOAD_FOLDER'], profile_img_name ))    
    profile_image.save(path)
    return {"message":'Done, successfully registred',"status":200} 

@app.route("/api/add/", methods=['POST'])
def addCow():
    global ACTUAL_IMAGE_ID
    requested_info = request.get_json()
    #print(requested_info)
    #valores obligatorios
    cow = {
        'name' : requested_info['name'],
        'mom' : requested_info['mom'],
        'dad' : requested_info['dad'],
        'weigth': requested_info['weigth'],
        'race': requested_info['race'],
        'age': requested_info['age'],
        'cowshed': requested_info['cowshed'],
        'state': requested_info['state'],
        'number_children' : [],
        'vacunas' : [],
        'image_id': requested_info['image_id']
    }
    print(cow)
    ACTUAL_IMAGE_ID = cow['image_id']
    exist = cows.find_one({'name':cow['name'],'dad':cow['dad'],'mom':cow['mom']})   

    if exist : return {"message":'cow already exist',"status":200}
    result = cows.insert_one(cow)
    qr = qrcode.make(str(result.inserted_id))
    qr.save("./static/cows/qrcodes/"+str(result.inserted_id)+".png", format="PNG")

    
    
    return {"message":'Done, successfully registred',"status":200}

@app.route('/api/get/', methods=['POST'])
def getinfo():

    requested_info = request.get_json()

    print(requested_info)

    id = requested_info['_id']



    cow = cows.find_one({"_id":ObjectId(id)})

    

    if not cow : return "cow doesn't exist", 404


    cow = json_util.dumps(cow)

    return cow,200

@app.route('/api/update/', methods=['POST'])
def updateInfo():
    requested_info = request.get_json()

    id = requested_info['id']
    cow = cows.find_one({'_id':ObjectId(id)})
    if not cow : return "cow doesn't exist", 404

    if requested_info['type'] == "vacunas":

        new_vacunas = requested_info['vacunas']

        cows.find_one_and_update({'_id':ObjectId(id)},{'$set':{'vacunas':new_vacunas}})
        return "vacunas updated successfully", 200
    
    if requested_info['type'] == "children":

        new_children = requested_info['number_children']

        cows.find_one_and_update({'_id':ObjectId(id)},{'$set':{'number_children':new_children}} )
        return "children updated successfully", 200
    
    if requested_info['type'] != "children" or requested_info['type'] != "vacunas":

        return "option not found", 404




    
    
    