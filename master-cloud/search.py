from math import sqrt
from operator import itemgetter
from numpy.linalg import norm
from csv import reader

def manhattan(a, b):
    return sum(abs(val1-val2) for val1, val2 in zip(a,b))

def euclidean(a,b) :
    return norm(a - b)

def topKSearch(query, K = 10) :
    similarity = []
    with open('metadb.csv') as file_obj:
        heading = next(file_obj)
        reader_obj = reader(file_obj)
        for row in reader_obj:
            id, f, R, shadows = row
            f = [float(val) for val in f.split(" ")]
            similarity.append({
                "id" : id,
                # "m_distance" : manhattan(query.reshape((4096,1)), image["features"].reshape((4096,1)))
                "m_distance" : manhattan(query, f)
            })
        file_obj.close()
        
    similarity = sorted(similarity, key=itemgetter('m_distance'))
    results = []
    for i in range(K) :
        results.append(similarity[i]["id"])
        # print(similarity[i]["id"])
    
    return results
    # return []