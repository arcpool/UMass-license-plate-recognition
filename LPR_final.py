#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 23:02:31 2020

@author: arya
"""
"""
@details: A project to fast process and recognize all the license plate numbers in UMass Parking services and 
          to check their validity in the UMass database of parking permits using two pre-defined models.
           
"""

import io
import glob
import os
from google.cloud import vision
from datetime import datetime
import pandas as pd
import requests
import base64
import json 

start_time = datetime.now()
directory = '/Users/arya/Desktop/LPR_Project/updatedSet'
counter = 1;

##iterating through the directory of images
for image_path in glob.iglob('/Users/arya/Desktop/LPR_Project/updatedSet/*.jpg'): 
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/arya/Desktop/LPR_Project/licenseplaterecognition007-90c1d10d6a08.json"
    client = vision.ImageAnnotatorClient()
    print(image_path)
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()

    # construct an image instance
    image = vision.types.Image(content=content)

    # annotate Image Response
    response = client.text_detection(image=image)  # returns TextAnnotation
    df = pd.DataFrame(columns=['locale', 'description'])

    texts = response.text_annotations
    for text in texts:
        df = df.append(
                dict(
                    locale=text.locale,
                    description=text.description
                    ),
                    ignore_index=True
                   )
                                
    indexList = [] #stores index of "Massachusetts"
    plateList = []
    nullList = []
    flag = True
    subStringM = "Massachusetts"
    subStringNH = "DIE"
    subStringR = "Island"
    
    def numCheck(s):
        return sum(c.isdigit() for c in s)

    plateList = df["description"]
    
    vt_ctr = 0; #Vermont license plate check
    for x in plateList:
        if x.lower() == "vermont":
            vt_ctr = vt_ctr + 1
            flag = False
            break
   
    if(vt_ctr > 0): # For Assigning Vermont Number Plate to plateNum
        plateNum = ""
        prevPlate = ""
        for k in plateList:
            if(k.isdigit()):
                plateNum = prevPlate + k
                flag = False
                break
            prevPlate = k
        
    # For states: NY, CT, and NH
    for y in range(1,len(plateList)):
        plateNum = ""
        prevPlate = ""
        if("-" in plateList[y]):
            plateNum = plateList[y]
        if(numCheck(plateNum) < 3):
            flag = False
            continue
        else:
            break
        prevPlate = plateList[y]
        
        
    if((plateNum == "") & (len(plateNum) < 3)): 
        flag = False
        plateNum = ""
        prevPlate = ""
        double_dig = 0
        for k in plateList:
            if(k.isdigit()):
                double_dig = double_dig + 1
                if double_dig == 1:
                    if(prevPlate.isalpha()):
                        plateNum = prevPlate + k
                        break
                    if double_dig == 2:
                        plateNum = prevPlate + k
                        break
            prevPlate = k
    
    if(subStringM in plateNum):
        flag = True


#   For states: MA, RI, NH, and others
    if(flag):           
        model = 'sk_e3bb5294b71b97fc4ad0d8cc'
        with open(image_path, 'rb') as image_file:
            img_base64 = base64.b64encode(image_file.read())
                                                                                  
        url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % (model)
        r = requests.post(url, data = img_base64)
        plateNum = (json.dumps(r.json()["results"][0]["plate"], indent=2))
    
    print(counter)   #index of the image  
    print(flag)                                                                         
    print("The License Plate number is: " + plateNum)  #recognized plate number 
    print("____________________________________________")
    plateNum = ""    
    counter = counter + 1
                 
print('Total time: {}'.format(datetime.now() - start_time))