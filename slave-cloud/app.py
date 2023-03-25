from flask import Flask, jsonify, request, make_response, send_from_directory
import traceback
from csv import writer, reader
from datetime import datetime
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = './data'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Route : GET /
# Desc  : To verify that the service is up
@app.route("/")
def hello () :
    return jsonify({
        "message" : "Hello from slave cloud" 
    })


# Route : POST /store/<id>
# Desc  : To store image shadow to the cloud
# Req   : shadow
# Resp  : success
@app.route("/store/<id>", methods=["POST"])
def storeShadow(id) :
    try:
        data = request.json
        shadow = data["shadow"]

        # Store shadow in data folder
        filename = id + ".txt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        
        with open(filepath, 'w') as shad_file :
            shad_file.write(shadow)

        log_entry = [id, datetime.now()]
        with open('store-logs.csv', 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(log_entry)
            f_object.close()
        
        return jsonify({"success": True})

    except Exception as err :
        print(''.join(traceback.format_exception(etype=type(err), value=err, tb=err.__traceback__)))
        return jsonify({"success" : False, "error" : err.__str__()})


# Route : GET /retrieve/<id>
# Desc  : To fetch image shadow from the cloud
# Req   : -
# Resp  : shadow
@app.route("/retrieve/<id>", methods=["GET"])
def getShadow(id) :
    # Check for the presence of shadow
    isPresent = False
    with open('store-logs.csv') as file_obj:
        heading = next(file_obj)
        reader_obj = reader(file_obj)
        for row in reader_obj:
            image_id, created_at = row
            if(image_id == id) :
                isPresent = True
                break
        file_obj.close()

    if(isPresent) :
        # Retrieve shadow
        filename = id + ".txt"
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    else :
        response = make_response(jsonify({
            "message" : "No shadow found"
        }), 404)
        return response


if __name__ == '__main__' :
    app.run(debug=True)