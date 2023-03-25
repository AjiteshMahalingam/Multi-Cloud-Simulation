from csv import reader
import requests
import random
import os

slave_clouds = [
    "slave-cloud-1:5000",
    "slave-cloud-2:5000",
    "slave-cloud-3:5000",
    "slave-cloud-4:5000",
    "slave-cloud-5:5000"
]

TEMP_FOLDER = "./temp"

def getRecord(image_id) :
    record = {}
    with open('metadb.csv') as file_obj:
        heading = next(file_obj)
        reader_obj = reader(file_obj)
        for row in reader_obj:
            id, f, R, shadows = row
            if image_id == id :
                record = {
                    "image_id" : id,
                    "feature_vector" : [float(val) for val in f.split(" ")],
                    "remainder_matrix" : R,
                    "shadows" : shadows
                }
                return record

def getShadows (image_id, k = 3) :
    results = []
    i = 0
    for cloud in random.sample(slave_clouds, k) :
        r = requests.get("http://" + cloud + "/retrieve/"+image_id)
        if(r.status_code == 200 ) : 
            filename = str(image_id) + "_shadow_" + str(i) + ".txt"
            filename = os.path.join(TEMP_FOLDER, filename)
            with open(filename, "wb") as text_file:
                text_file.write(r.content)
            results.append(filename)
        i += 1
    return results

def storeShadow(image_id, shadows) :
    # print(shadows)
    results = {}
    shadows_len = 5
    for i in range(shadows_len) :
        url = "http://" + slave_clouds[i] + "/store/" + str(image_id)
        # files = { "shadow" : shadows[i]}
        # r = requests.post(url, files=files)
        r = requests.post(url, json = {"shadow" :shadows[str(i)]})
        if(r.json()["success"]) :
            results[i] = slave_clouds[i]
        else :
            results[i] = None
        
    return results
                
