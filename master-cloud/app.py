from flask import Flask, jsonify, request
import traceback
from models.metarecord import MetaRecord
from csv import writer
from search import topKSearch
from reconstructImage import reconstruct_image
from utils import getRecord, getShadows, storeShadow
import os

TEMP_FOLDER = "./temp"
DATA_FOLDER = "./data"

app = Flask(__name__)
app.config["TEMP_FOLDER"] = TEMP_FOLDER
app.config["DATA_FOLDER"] = DATA_FOLDER


# Route : GET /
# Desc  : To verify that the service is up
@app.route("/")
def hello () :
    return jsonify({
        "message" : "Hello from master cloud" 
    })

# Route : POST /upload
# Desc  : To upload an encrypted image to the cloud
# Req   : feature_vector, remainder_matrix, shadows
# Resp  : image_id, shadow_refs 
@app.route("/upload", methods=["POST"])
def uploadImage() :
    try:
        # Get data from request
        data = request.json
        id = data["id"]
        features = data["features"][0]
        rem_matrix = data["remainder_matrix"]
        shadows = data["shadows"]
        
        # Create meta db record
        new_record = MetaRecord(id, features)
        
        # Store remainder matrix
        filepath = os.path.join(app.config["DATA_FOLDER"], new_record.remainder_matrix)
        with open(filepath, 'w') as rem_file :
            rem_file.write(rem_matrix)

        # Store shadows
        new_record.shadows = storeShadow(new_record.image_id, shadows)

        # Store meta record
        with open('metadb.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(new_record.tolist())
        
        return jsonify({"id" : new_record.image_id, "shadows" : new_record.shadows})

    except Exception as err :
        print(''.join(traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__)))
        return jsonify({"error" : err.__str__()})


# Route : GET /query
# Desc  : To fecth similar images
# Req   : feature_vector of query image
# Resp  : Reconstructed encrypted similar images
@app.route("/query", methods=["POST"])
def queryImage() :
    try :
        # Get data from request
        data = request.json
        query_features = data["features"][0]

        # Top K Search
        similar_ids = topKSearch(query_features)
        results = []
        for id in similar_ids :
            # Fetch shadows and reconstruct
            record = getRecord(id)
            shadows = getShadows(id, 3)
            remainder_matrix = os.path.join(app.config["DATA_FOLDER"], record["remainder_matrix"])
            
            # Reconstruct image
            reconst_image = reconstruct_image(id, remainder_matrix, shadows)

            with open(reconst_image, "r") as file_obj :
                results.append({
                    "image_id" : id,
                    "data" : file_obj.read()
                })
        
        # clear out temp folder
        for file in os.listdir(app.config["TEMP_FOLDER"]) :
            file_path = os.path.join(app.config["TEMP_FOLDER"], file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

        return jsonify({"results": results})

    except Exception as err :
        print(''.join(traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__)))
        return jsonify({"error" : err.__str__()})


if __name__ == '__main__' :
    app.run(debug=True)