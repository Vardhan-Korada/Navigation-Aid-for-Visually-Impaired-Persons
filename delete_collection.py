import boto3


def delete_collection(collection_id):
    res = boto3.client("rekognition").delete_collection(CollectionId=collection_id)
    print(res["StatusCode"])


delete_collection("Faces")