import uuid

class MetaRecord() :
    image_id = ""
    feature_vector = []
    remainder_matrix = ""
    shadows = {}

    def __init__(self, id, f):
        # self.image_id = str(uuid.uuid4())
        self.image_id = id
        self.feature_vector = f
        self.remainder_matrix = self.image_id + "_remainder_img.txt"
        # for shadow in shadows :
        #     self.shadows[shadow] = None

    def __str__(self):
        print(self.image_id)
        print(self.feature_vector)
        print(self.remainder_matrix)
        print(self.shadows)

    def tolist(self) :
        return [
            self.image_id, 
            ' '.join([str(elem) for elem in self.feature_vector]), 
            self.remainder_matrix, 
            self.shadows
            ]

# testRecord = MetaRecord()