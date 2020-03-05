# Author: Yap June Wai
# Date: 5 August 2019
# Description: To read the .csv data file for lead detection project


# Imports
import os
import sys
import glob
import cv2
import json
import pandas as pd
from enum import Enum
from helper import trace, RetrieveColsInDf, RemoveRowsInDF, RetrieveRowsInDf
import argparse

# Define
_DEBUG = 0

# Enum Definition ------------------------------------------------------|
class Label(Enum):
    pins = 0 # Component RefDes
    body = 1 # Component Package

# END Enum Definition ---------------------------------------------------|

def GenAllImagesWithBBox(img_file, tst_dir, data, tileno):
    font                   = cv2.FONT_HERSHEY_COMPLEX
    fontScale              = 1
    scaleFactor            = 0.02##CHANGE FOR DIFFERENT SIZE IN RELATION TO HEIGHT
    fontColor              = (0,0,0)
    fontColorSearchArea    = (0,255,255)
    fontColorBody          = (0,255,0)
    fontColorPins          = (230,255,0)
    lineType               = 2

    img = cv2.imread(img_file)
    outimg = os.path.join(tst_dir, os.path.basename(img_file).replace(".jpg","_{}.jpg".format(tileno)))
    trace(outimg)

    ### Add Here
    for index, row in data.iterrows():
        if(row['searchArea']):
            data = json.loads(row['searchArea'])
        
            fontColor = fontColorSearchArea
            x1 =  data[0]
            y1 =  data[1]
            x2 =  data[2]
            y2 =  data[3]
            
            #print(x1)
            p1 = (int(x1), int(y1))
            p2 = (int(x2), int(y2))
            cv2.rectangle(img, p1,p2, fontColor, 3)
            if(row['refDes']):
                cv2.putText(img, row['refDes'], (x1,y1-10),\
                   font, fontScale, fontColor, lineType)
            
        if(row['body_dims']):
            fontColor = fontColorBody
            data = json.loads(row['body_dims'])
            #print(data)

            x1 =  data[0]
            y1 =  data[1]
            x2 =  data[2]
            y2 =  data[3]
            
            centroid_x = data[7]
            centroid_y = data[8]
            #print(x1)
            p1 = (int(x1), int(y1))
            p2 = (int(x2), int(y2))
            cv2.rectangle(img, p1,p2, fontColor, 3)
            cv2.circle(img, (centroid_x, centroid_y), 5, fontColorBody, 3) 
            
        if(row['pins_dims']):
            fontColor = fontColorPins
            data_list = json.loads(row['pins_dims'])
            if(data_list):
                for data in data_list:
                    x1 =  data[0]
                    y1 =  data[1]
                    x2 =  data[2]
                    y2 =  data[3]
                    p1 = (int(x1), int(y1))
                    p2 = (int(x2), int(y2))
                    cv2.rectangle(img, p1,p2, fontColor, 3)
        # fontScale=max (row['dy'],row['dx'])*scaleFactor
        
        cv2.imwrite(outimg, img)
    print("[SUCCESS]: Image bbox overlay completed!")


# Pins Maninulation --------------------------------------|
# *************************************************************
#   Author       : JW
#   Description	 : pins is 2D list
#   whereas bodydims is 1D list
#   As one component has one body only, but can has multiple pins
#   For extracting the pins coordinate relative to the center of the 
#   body.
#   Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************
def ExtractPinsCoordinateRelativ2BodyCentroid(pins:list, bodydims: list):
    
    pin_list = []
    if pins:
        for pin in pins:
            body_centroid_x = bodydims[7]
            body_centroid_y = bodydims[8]

            pin_x1 = pin[0] - body_centroid_x
            pin_y1 = pin[1] - body_centroid_x
            pin_x2 = pin[2] - body_centroid_y
            pin_y2 = pin[3] - body_centroid_y
            pin_w  = pin[4]
            pin_h = pin[5]

            pin_list.append([pin_x1, pin_y1, pin_x2, pin_y2, pin_w, pin_h])
    
    return pin_list

def WritePinsCoordinateRelative2BodyCentroid(data_df, fname = "PinsCoordinateRelative2BodyCentroid.csv"):
    pin_list_new = [] 
    for index, row in data_df.iterrows():
        body_list = []
        pin_list = []
        if(row['body_dims']):
            body_list = json.loads(row['body_dims'])
        
        if(row['pins_dims']):
            pin_list = json.loads(row['pins_dims'])
            
        pin_list = ExtractPinsCoordinateRelativ2BodyCentroid(pin_list, body_list)
        pin_list_new.append(pin_list)
    
    data_df["pins_dims"] = pin_list_new
    output_file_csv = os.path.join(INPUT_TXT_DIR_PATH, fname)
    data_df.to_csv(output_file_csv,index=False)
# End Pins Maninulation --------------------------------------|

def SaveAllComponentImagesInTile(root_dir, tile_csvpath, boardname, output_dir):
    try:
        tile_info_df = pd.read_csv(tile_csvpath, delimiter=",")
    except:
        raise ValueError("Failed to load {}".format(tile_csvpath))
        sys.exit()

    # Settings
    font                   = cv2.FONT_HERSHEY_COMPLEX
    fontScale              = 1
    scaleFactor            = 0.02##CHANGE FOR DIFFERENT SIZE IN RELATION TO HEIGHT
    fontColor              = (0,0,0)
    fontColorSearchArea    = (0,255,255)
    fontColorBody          = (0,255,0)
    fontColorPins          = (230,255,0)
    lineType               = 2

    # Iterate
    for itileinfodf, row in tile_info_df.iterrows():

        if (row['pin_num']):
            #Load all images
            selected_image_dir = os.path.dirname(  row['path'][:-1] if row['path'].endswith("/") else row['path']) # -1 for mistakes in csv, done to skip end slash
            full_selected_image_dir=os.path.join(root_dir, selected_image_dir)
            jpg_paths = [f for f in glob.glob(full_selected_image_dir + "/*.jpg", recursive=True)]
            pmg_paths = [f for f in glob.glob(full_selected_image_dir + "/*.pgm", recursive=True)]
            print("Extracting {} Board|\t {}\t|\t {} pins|\t {} ".format(boardname, row['refDes'], row['pin_num'],row['package']))

            # Crop image
            searchArea=[]
            label_list=[]
            line=""
            if(row['searchArea']):
                data = json.loads(row['searchArea'])
                x1 =  data[0]
                y1 =  data[1]
                x2 =  data[2]
                y2 =  data[3]
                searchArea = data
                
                # Read PGM
                for i, p in enumerate(pmg_paths):
                    img = cv2.imread(p, cv2.IMREAD_UNCHANGED)  
                    cropped_img = img[y1:y2, x1:x2] 
                    pgm_name = boardname+'_'+row['refDes'].replace(':','')+'_'+str(i)+'.pgm'
                    pgmcomment_name = boardname+'_'+row['refDes'].replace(':','')+'_'+str(i)+'.war'
                    cv2.imwrite(os.path.join(output_dir, pgm_name), cropped_img)

                    # Comments: Warpage componsation information
                    with open(p, 'rb') as f, open (os.path.join(output_dir, pgmcomment_name), 'w') as g:
                        comments=[]
                        for nline in range (6):
                            line = f.readline()
                            if (line.startswith(b'#')):
                                g.write(line.decode('ascii'))

                # Read JPG
                for i, p in enumerate(jpg_paths):
                    img = cv2.imread(p)  
                    cropped_img = img[y1:y2, x1:x2] 
                    name = boardname+'_'+row['refDes'].replace(':','')+'_'+str(i)+'.jpg'
                    cv2.imwrite(os.path.join(output_dir,name), cropped_img)

                    # Debug
                    if(_DEBUG & 3):
                        p1 = (int(x1), int(y1))
                        p2 = (int(x2), int(y2))
                        cv2.rectangle(img, p1,p2, fontColorSearchArea, 3)
                        if(row['refDes']):
                            cv2.putText(img, row['refDes'], (x1,y1-10), font, fontScale, fontColorSearchArea, lineType)


            # Body dims
            bodydims=[]
            if(row['body_dims']):
                bodydims = json.loads(row['body_dims'])
                x1 =  bodydims[0] - searchArea[0]
                y1 =  bodydims[1] - searchArea[1]
                x2 =  bodydims[2] - searchArea[0]
                y2 =  bodydims[3] - searchArea[1]   
                line="{},{},{},{},{}".format(x1,y1,x2,y2, Label.body.value)
                label_list.append(line)

                if(_DEBUG & 3):
                    x1 =  bodydims[0]
                    y1 =  bodydims[1]
                    x2 =  bodydims[2]
                    y2 =  bodydims[3]                
                    centroid_x = bodydims[7]
                    centroid_y = bodydims[8]
                    
                    p1 = (int(x1), int(y1))
                    p2 = (int(x2), int(y2))
                    cv2.rectangle(img, p1,p2, fontColor, 3)
                    cv2.circle(img, (centroid_x, centroid_y), 5, fontColorBody, 3) 

            # Pins dims
            if(row['pins_dims']):
                data_list = json.loads(row['pins_dims'])
                # data_list = ExtractPinsCoordinateRelativ2BodyCentroid(data_list, bodydims)
                if(data_list):
                    for data in data_list:
                        x1 =  data[0] - searchArea[0]
                        y1 =  data[1] - searchArea[1]
                        x2 =  data[2] - searchArea[0]
                        y2 =  data[3] - searchArea[1]
                        line = "{},{},{},{},{}".format(x1,y1,x2,y2,Label.pins.value)
                        label_list.append(line)
                        
                        # Debug
                        if(_DEBUG & 3):
                            x1 =  data[0]
                            y1 =  data[1]
                            x2 =  data[2]
                            y2 =  data[3]
                            p1 = (int(x1), int(y1))
                            p2 = (int(x2), int(y2))
                            cv2.rectangle(img, p1,p2, fontColorPins, 3)

            #Write Labels
            name = boardname+'_'+row['refDes'].replace(':','')+'.txt'
            label_path = os.path.join(output_dir,name)
            with open(label_path ,'w') as f:
                for element in label_list:
                    f.write(element)
                    f.write("\n")

            # Save image
            if(_DEBUG & 3):
                x1 =  max (searchArea[0]-100 ,0)
                y1 =  max (searchArea[1]-100, 0)
                x2 =  min(searchArea[2]+100, img.shape[0])
                y2 =  min (searchArea[3]+100, img.shape[1])
                cv2.imshow("Search area", img[y1:y2, x1:x2])
                cv2.waitKey(0) # waits until a key is pressed
                cv2.destroyAllWindows() # destroys the window showing image
            


# *************************************************************
#   Author       : HM Fazle Rabbi
#   Description  : Function to read the all_tiles.csv and print the
#   bbox on top of it.
#   Date Modified: 
#   Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************
def OverlayBBoxesTileImages_legacy(root_dir, tile_csvpath, boardname, output_dir):

    #Directory
    ROOT_DIR = os.getcwd()
    BASE_DIR = os.path.join(ROOT_DIR, "Board", "16561-3_B")
    BASE_DIR = "D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files/9611GCR2-T-7"
    INPUT_IMG_KEY = "Tiles"
    OUTPUT_IMG_KEY = "bbox"

    #Arguments
    if (len (sys.argv) > 1):
        INPUT_IMG_DIR_PATH = sys.argv[1]  #os.path.join(BASE_DIR, INPUT_IMG_KEY)
        INPUT_TXT_DIR_PATH = sys.argv[2] #os.path.join(BASE_DIR, "output")
        OUTPUT_IMG_DIR_PATH = os.path.join(sys.argv[3], OUTPUT_IMG_KEY)
    else:
        trace ("Executing with default values.")
        INPUT_IMG_DIR_PATH = os.path.join(BASE_DIR, INPUT_IMG_KEY)
        INPUT_TXT_DIR_PATH = os.path.join(BASE_DIR, "output")
        OUTPUT_IMG_DIR_PATH = os.path.join(BASE_DIR, OUTPUT_IMG_KEY)

    if not os.path.exists(OUTPUT_IMG_DIR_PATH):
        os.mkdir(OUTPUT_IMG_DIR_PATH)
    trace("INPUT_IMG_DIR_PATH {}\nINPUT_TXT_DIR_PATH {}\nOUTPUT_IMG_DIR_PATH {}\n".format(INPUT_IMG_DIR_PATH, INPUT_TXT_DIR_PATH, OUTPUT_IMG_DIR_PATH), _DEBUG)
    

    #Load all Tile Directories Like 0,1,2,.....
    tile_dir_basepath=os.path.join(root_dir, boardname,"Tiles")
    TILES_DIR_PATH = [os.path.join(tile_dir_basepath, file) for file in os.listdir(tile_dir_basepath) if not os.path.isfile(os.path.join(tile_dir_basepath, file))] 
    trace("TILES_DIR_PATH:\n", _DEBUG)
    for x in TILES_DIR_PATH: trace("\t{}".format(x), _DEBUG)

    #Tile Directory
    INPUT_TEXT_FILES_PATH = []
    for txtfolder in os.listdir(INPUT_TXT_DIR_PATH):
        if os.path.isdir(os.path.join(INPUT_TXT_DIR_PATH, txtfolder)):
            for txtfile in os.listdir(os.path.join(INPUT_TXT_DIR_PATH, txtfolder)):
                if txtfile.endswith(".txt"):
                    INPUT_TEXT_FILES_PATH.append(os.path.join(INPUT_TXT_DIR_PATH, txtfolder, txtfile)) # Sample: D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files/9611GCR2-T-7/output/0/processed_tile_0.txt
    
    for f in INPUT_TEXT_FILES_PATH:
        try:
            info_df = pd.read_csv(f, delimiter=",", \
                                names=["path", "refDes", "package", "searchArea", \
                                        "body_dims", "ocv_mark","pins_dims", "pins_no", \
                                        "rep_type", "errMessage"] )
        except:
            print("ERROR: Image: %s.jpg failed"%(f))
            sys.exit()
        #WritePinsCoordinateRelative2BodyCentroid(info_df)
        info_df = RemoveRowsInDF(info_df, 'unknown')
        # code for tile number need to update
        tile_no = f.replace(".txt","").split("_")[-1]
        img_dir = os.path.join(INPUT_IMG_DIR_PATH, tile_no)
        input_img_path =  [ img for img in glob.glob(img_dir  + "/*_RGB.jpg", recursive=True)]
        
        #print(input_img_path)
        for img_path in input_img_path:
            
            GenAllImagesWithBBox(img_path, OUTPUT_IMG_DIR_PATH, info_df, tile_no)

def OverlayBBoxesTileImages_(root_dir, tile_csvpath, boardname, output_dir):
#   Unfinished
  
  try:
        tile_info_df = pd.read_csv(tile_csvpath, delimiter=",")
        tile_info_df.sort_values(by=['path'])
    except:
        raise ValueError("Failed to load {}".format(tile_csvpath))
        sys.exit()

    # Settings
    font                   = cv2.FONT_HERSHEY_COMPLEX
    fontScale              = 1
    scaleFactor            = 0.02##CHANGE FOR DIFFERENT SIZE IN RELATION TO HEIGHT
    fontColor              = (0,0,0)
    fontColorSearchArea    = (0,255,255)
    fontColorBody          = (0,255,0)
    fontColorPins          = (230,255,0)
    lineType               = 2

    # Iterate
    for itileinfodf, row in tile_info_df.iterrows():

        if (row['pin_num']):
            #Load all images
            selected_image_dir = os.path.dirname(  row['path'][:-1] if row['path'].endswith("/") else row['path']) # -1 for mistakes in csv, done to skip end slash
            full_selected_image_dir=os.path.join(root_dir, selected_image_dir)
            jpg_paths = [f for f in glob.glob(full_selected_image_dir + "/*_RGB.jpg", recursive=True)]
            print("Extracting {} Board|\t {}\t|\t {} pins|\t {} ".format(boardname, row['refDes'], row['pin_num'],row['package']))

            # Crop image
            searchArea=[]
            label_list=[]
            line=""
            if(row['searchArea']):
                data = json.loads(row['searchArea'])
                x1 =  data[0]
                y1 =  data[1]
                x2 =  data[2]
                y2 =  data[3]
                searchArea = data
                
                # Read JPG
                for i, p in enumerate(jpg_paths):
                    img = cv2.imread(p)  
                    cropped_img = img[y1:y2, x1:x2] 
                    name = boardname+'_'+row['refDes'].replace(':','')+'_'+str(i)+'.jpg'
                    cv2.imwrite(os.path.join(output_dir,name), cropped_img)

                    # Debug
                    if(_DEBUG & 3):
                        p1 = (int(x1), int(y1))
                        p2 = (int(x2), int(y2))
                        cv2.rectangle(img, p1,p2, fontColorSearchArea, 3)
                        if(row['refDes']):
                            cv2.putText(img, row['refDes'], (x1,y1-10), font, fontScale, fontColorSearchArea, lineType)


            # Body dims
            bodydims=[]
            if(row['body_dims']):
                bodydims = json.loads(row['body_dims'])
                x1 =  bodydims[0] - searchArea[0]
                y1 =  bodydims[1] - searchArea[1]
                x2 =  bodydims[2] - searchArea[0]
                y2 =  bodydims[3] - searchArea[1]   
                line="{},{},{},{},{}".format(x1,y1,x2,y2, Label.body.value)
                label_list.append(line)

                if(_DEBUG & 3):
                    x1 =  bodydims[0]
                    y1 =  bodydims[1]
                    x2 =  bodydims[2]
                    y2 =  bodydims[3]                
                    centroid_x = bodydims[7]
                    centroid_y = bodydims[8]
                    
                    p1 = (int(x1), int(y1))
                    p2 = (int(x2), int(y2))
                    cv2.rectangle(img, p1,p2, fontColor, 3)
                    cv2.circle(img, (centroid_x, centroid_y), 5, fontColorBody, 3) 

            # Pins dims
            if(row['pins_dims']):
                data_list = json.loads(row['pins_dims'])
                # data_list = ExtractPinsCoordinateRelativ2BodyCentroid(data_list, bodydims)
                if(data_list):
                    for data in data_list:
                        x1 =  data[0] - searchArea[0]
                        y1 =  data[1] - searchArea[1]
                        x2 =  data[2] - searchArea[0]
                        y2 =  data[3] - searchArea[1]
                        line = "{},{},{},{},{}".format(x1,y1,x2,y2,Label.pins.value)
                        label_list.append(line)
                        
                        # Debug
                        if(_DEBUG & 3):
                            x1 =  data[0]
                            y1 =  data[1]
                            x2 =  data[2]
                            y2 =  data[3]
                            p1 = (int(x1), int(y1))
                            p2 = (int(x2), int(y2))
                            cv2.rectangle(img, p1,p2, fontColorPins, 3)

            #Write Labels
            name = boardname+'_'+row['refDes'].replace(':','')+'.txt'
            label_path = os.path.join(output_dir,name)
            with open(label_path ,'w') as f:
                for element in label_list:
                    f.write(element)
                    f.write("\n")

            # Save image
            if(_DEBUG & 3):
                x1 =  max (searchArea[0]-100 ,0)
                y1 =  max (searchArea[1]-100, 0)
                x2 =  min(searchArea[2]+100, img.shape[0])
                y2 =  min (searchArea[3]+100, img.shape[1])
                cv2.imshow("Search area", img[y1:y2, x1:x2])
                cv2.waitKey(0) # waits until a key is pressed
                cv2.destroyAllWindows() # destroys the window showing image

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--root_fpath", default=os.path.normpath("D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files"))
    parser.add_argument("--boardname", default="9611GCR2-T-7")
    parser.add_argument("--tile_csvpath", default=os.path.normpath("D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files/9611GCR2-T-7/output/all_tiles.csv"))
    parser.add_argument("--output_dir", default=os.path.normpath("D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files/9611GCR2-T-7/output_images"))
    flags = parser.parse_args()


    option=1
    if(option ==1):
        SaveAllComponentImagesInTile(root_dir=flags.root_fpath, tile_csvpath=flags.tile_csvpath, boardname=flags.boardname,output_dir=flags.output_dir)
    