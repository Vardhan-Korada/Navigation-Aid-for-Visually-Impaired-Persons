import boto3


def create_collection(collection_id):
    res = boto3.client("rekognition").create_collection(CollectionId=collection_id)
    print(res["StatusCode"])


create_collection("Faces")
