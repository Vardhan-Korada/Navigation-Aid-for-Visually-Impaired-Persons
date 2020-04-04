import boto3


def search_face(collection_id,threshold,image_path):
    try:
        with open(image_path,"rb") as image:
            res = boto3.client("rekognition").search_faces_by_image(
                CollectionId=collection_id,
                FaceMatchThreshold=threshold,
                Image={"Bytes":image.read()}
                )
            res = res["FaceMatches"]
            if len(res) == 0:
                print("No matches found...")
                return
            print(len(res),"matches found with ...")
            for i in range(len(res)):
                print(str(i)+".","Similarity:",res[i]["Similarity"])
                print(str(i)+".","Confidence:",res[i]["Face"]["Confidence"])
    except:
        print("Image path doesn't exists")

search_face("Faces",92,"/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source2.jpg")