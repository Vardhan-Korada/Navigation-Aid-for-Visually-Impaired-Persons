import boto3


def index_faces(collection_id,image_path):
    try:
        with open(image_path,"rb") as image: 
            res = boto3.client("rekognition").index_faces(
                CollectionId=collection_id,
                Image = {"Bytes":image.read()}
            )
            print(res)
    except:
        pass


if __name__ == "__main__":
    print(boto3.client("rekognition").describe_collection(CollectionId="Faces"))
    for i in range(1,5):
        path = "/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source"+str(i)+".jpg"
        #index_faces("Faces",path)
    res = boto3.client("rekognition").list_faces(CollectionId="Faces")
    res = res["Faces"]
    print(len(res))
    face_ids = []
    for i in range(len(res)):
        face_ids.append(res[i]["FaceId"])
    print(face_ids)