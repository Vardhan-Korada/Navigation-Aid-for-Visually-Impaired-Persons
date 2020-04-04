# Python SDK for Amazon
import boto3
import os
import pytesseract
from PIL import Image
import pyphotoclick
import serial               
from time import sleep
import RPi.GPIO as GPIO


#Constants
ID_FILE_PATH = "/home/vardhan/Chandu-Vardhan/Face_Recognition/face_ids.txt"
SOURCE_IMAGE_PATH = "/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source42.jpg"
button1 = 16
button2 = 18
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0
gps_dict = {}


#Loading the face_ids and their names
f = open(ID_FILE_PATH,"r")
ids = f.read()
if ids == "":
    face_ids = {}
else:
    face_ids = eval(ids)
f.close()


#Function for creating a new collection
def create_collection(collection_id):
    res = boto3.client("rekognition").create_collection(CollectionId=collection_id)
    print(res["StatusCode"])


#Function for deleting a collection
def delete_collection(collection_id):
    res = boto3.client("rekognition").delete_collection(CollectionId=collection_id)
    print(res["StatusCode"])


#Function for adding a face to the collection
def index_faces(collection_id,image_path):
    try:
        with open(image_path,"rb") as image: 
            res = boto3.client("rekognition").index_faces(
                CollectionId=collection_id,
                Image = {"Bytes":image.read()}
            )
            return res["FaceRecords"][0]["Face"]["FaceId"]
    except:
        pass


#Function with more suitable name for adding a face
def add_face(collection_id,image_path):
    return index_faces(collection_id,image_path)
            

#Function for comparing the source image with database
def search_face(collection_id,threshold,image_path):
    try:
        with open(image_path,"rb") as image:
            new_res = boto3.client("rekognition").detect_faces(
                Image={"Bytes":image.read()}
                )
            if len(new_res["FaceDetails"]) == 0:
                return -9999
            image.close()
        with open(image_path,"rb") as image:
            res = boto3.client("rekognition").search_faces_by_image(
                CollectionId=collection_id,
                FaceMatchThreshold=threshold,
                Image={"Bytes":image.read()}
                )
            res = res["FaceMatches"]
            if len(res) == 0:
                print("No matches found...")
                return 0
            print(len(res),"matches found with ...")
            for i in range(len(res)):
                print(str(i+1)+".","Similarity:",res[i]["Similarity"])
                print(str(i+1)+".","Confidence:",res[i]["Face"]["Confidence"])
                print("It may be "+face_ids[res[i]["Face"]["FaceId"]])
                say_it("It may be "+face_ids[res[i]["Face"]["FaceId"]]+" with "+str(round(res[i]["Similarity"]))+" percent similarity")
            return len(res)
    except:
        print("Image path doesn't exists")


def add_new_face(collection_id,path):
    id = add_face(collection_id,path)
    face_ids[id] = input("Enter a name: ")
    f = open(ID_FILE_PATH,"w")
    f.write(str(face_ids))
    f.close()


def detect_text(path):
    try:
        with open(path,"rb") as image:
            res = boto3.client("rekognition").detect_text(
                Image = {"Bytes":image.read()}
                )
            res = res["TextDetections"]
            detected_texts = []
            for i in range(len(res)):
                sent = res[i]["DetectedText"]
                if res[i]["Type"] == "WORD":
                    continue
                detected_texts.append(sent+" ")
            return detected_texts
    except:
        print("Text processing failed..")


def tes_detect_text(path):
    try:
        res = pytesseract.image_to_string(Image.open(path))
        say_it(res)
    except:
        print("Text processing failed..")


def say_it(sent):
    re = boto3.client("translate").translate_text(
        Text=sent,
        SourceLanguageCode="en",
        TargetLanguageCode="hi"
        )
    sent = re["TranslatedText"]
    res = boto3.client("polly").synthesize_speech(
        VoiceId="Aditi",
        OutputFormat="mp3",
        Text=sent
        )
    file = open("speech.mp3","wb")
    file.write(res["AudioStream"].read())
    os.system("mpg123 "+"speech.mp3")
    file.close()


def setup():
       GPIO.setmode(GPIO.BOARD)
       GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
       GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def init_face_id():
    # delete_collection("Faces")
    # create_collection("Faces")
    # for i in range(1,5):
    #     path = "/home/vardhan/Chandu-Vardhan/Face_Recognition/faces/source"+str(i)+".jpg"
    #     index_faces("Faces",path)
    path = SOURCE_IMAGE_PATH
    text = detect_text(path)
    #tes_detect_text(path)
    matches = search_face("Faces",92,path)
    if len(text) == 0:
        print("No text is present")
        say_it("No text present in the image")
    else:
        tot = ""
        for sent in text:
            tot += sent
        print(tot)
        say_it(tot)
    #Adding a new face to the collection
    if matches == -9999:
        print("No face is present in the image...")
        say_it("No face is present in the image...")
    elif matches == 0:
        say_it("Do you want to create a new record for the new face?: ")
        ans = input("Do you want to create a new record for the new face?: ")
        if ans in "YyYesyesYES":
            add_new_face("Faces",path)
        else:
            pass
        print("Job Done...")


def find_gps_fix():
    gpgga_info = "$GPGGA,"
    ser = serial.Serial ("/dev/ttyS0")              
    GPGGA_buffer = 0
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    received_data = (str)(ser.readline())                   #read NMEA string received
    GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string                 
    if (GPGGA_data_available>0):
        GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string 
        NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
        GPS_Info()                                          #get time, latitude, longitude
        if gps_dict.get(str(lat_in_degrees)+str(long_in_degrees)) != None:
            print("You are at "+gps_dict[str(lat_in_degrees)+str(long_in_degrees)])
            say_it("You are at "+gps_dict[str(lat_in_degrees)+str(long_in_degrees)])
        else:
            print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
            say_it("Latitude "+str(lat_in_degrees)+" Longitude "+str(long_in_degrees))
    ans = input("Do you want to mark this location? (Y or N): ")
    say_it("Do you want to mark this location?")
    if ans == "Y":
        name = input("Enter the name of location: ")
        gps_dict[str(lat_in_degrees)+str(long_in_degrees)] = name


def GPS_Info():
    global NMEA_buff
    global lat_in_degrees
    global long_in_degrees
    nmea_time = []
    nmea_latitude = []
    nmea_longitude = []
    nmea_time = NMEA_buff[0]                    #extract time from GPGGA string
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string
    print("NMEA Time: ", nmea_time,'\n')
    print ("NMEA Latitude:", nmea_latitude,"NMEA Longitude:", nmea_longitude,'\n')
    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation
    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format


def convert_to_degrees(raw_value):
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position


if __name__ == "__main__":
    setup()
    while True:
        button1_state = GPIO.input(button1)
        button2_state = GPIO.input(button2)
        if button1_state == False:
            say_it("Face recognition initiated")
            init_face_id()
            say_it("Face recognition complete")
        elif button2_state == False:
            say_it("GPS Fix initiated")
            find_gps_fix()
            say_it("GPS Fix done")
