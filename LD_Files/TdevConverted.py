# Author: Yap June Wai
# Date: 5 August 2019
# Description: To convert the raw data file (.tdev, .rep) to csv for lead detection project

#____________________________Defining_Import_Package_Start_______________
# Imports ------------------------------------------------------|
import os
import glob
import pandas as pd
from enum import Enum
import sys
import argparse
from helper import trace
# End: Imports -------------------------------------------------|

# Define
_DEBUG=1

# Enum Definition ------------------------------------------------------|
class Component(Enum):
    refdes = 0 # Component RefDes
    package = 1 # Component Package
    # Search Area Metadata
    coordinate_x1 = 2 # x1
    coordinate_y1 = 3 # y1
    coordinate_x2 = 4 # x2
    coordinate_y2 = 5 # y2
    coordinate_c1 = 6 # centroid_x
    coordinate_c2 = 7 # centroid_y

class Pin(Enum):
    # Pin Metadata
    coordinate_x1 = 1 # pin x1
    coordinate_y1 = 2 # pin y1
    coordinate_x2 = 3 # pin x2
    coordinate_y2 = 4 # pin y2
    pin_w = 5 # pin width
    pin_h = 6 # pin height / pin length
    
class Body(Enum):
    # Body Metadata
    coordinate_x1 = 1 # body x1
    coordinate_y1 = 2 # bddy y1
    coordinate_x2 = 3 # body x2
    coordinate_y2 = 4 # body y2
    body_w = 5 # body width
    body_h = 6 # body height/ body length
    body_angle = 7 # body angle

class OCV(Enum):
    ocv_status = 1 # ocv_flag
# End: Enum Definition ------------------------------------------ ----|



# Helper functions  --------------------------------------------------|
def splitLineToList(line:str, sep = ";"):
    
    if(line.find("/") > 0):
        line = line[0:line.find("/")] #Skip comments

    line = line.strip()
    info = line.replace(":",sep).split(sep)
    return info, len(info)
# End: Helper functions  ---------------------------------------------|



# Extract DF functions ----------------------------------------|
# /*************************************************************
# *     Author          : JW
# *	    Description		: Info Extractor and parsers
# *     Last Modified   : 20190806_1342
# *     Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************/    
def extractComponentInfo(line:str):
    if (line.find("/") > 0):
        line = line[0:line.find("/")]
    
    componentInfo = line.split(";")
    
    refdes_data = componentInfo[Component.refdes.value]
    package_data = componentInfo[Component.package.value]
    
    component_x1 = int(componentInfo[Component.coordinate_x1.value])
    component_y1 = int(componentInfo[Component.coordinate_y1.value])
    component_x2 = int(componentInfo[Component.coordinate_x2.value])
    component_y2 = int(componentInfo[Component.coordinate_y2.value])
    component_centroid_x = int(componentInfo[Component.coordinate_c1.value])
    component_centroid_y = int(componentInfo[Component.coordinate_c2.value])
    
    searchArea_data = [ component_x1, \
                        component_y1, \
                        component_x2, \
                        component_y2, \
                        component_centroid_x, \
                        component_centroid_y  \
                      ]
    trace("refdes_data:{} searchArea_data: {}".format(refdes_data, searchArea_data), _DEBUG)
    return refdes_data, package_data, searchArea_data

def extractBodyInfo(line:str):
    # Extract the body coordinate for top-left, bottom-right, body-width, body-height, and angle
    bodyInfo, bodyInfo_len = splitLineToList(line, ";")
    
    body_coordinate_x1 = int(bodyInfo[Body.coordinate_x1.value])
    body_coordinate_y1 = int(bodyInfo[Body.coordinate_y1.value])
    body_coordinate_x2 = int(bodyInfo[Body.coordinate_x2.value])
    body_coordinate_y2 = int(bodyInfo[Body.coordinate_y2.value])
    
    body_w = int(bodyInfo[Body.body_w.value])
    body_h = int(bodyInfo[Body.body_h.value])
    body_angle = int(bodyInfo[Body.body_angle.value])
    
    body_centroid_x = int((body_coordinate_x1 + body_coordinate_x2) / 2)
    body_centroid_y = int((body_coordinate_y1 + body_coordinate_y2) / 2)
    
    bodyInfo_data = [ body_coordinate_x1, \
                      body_coordinate_y1, \
                      body_coordinate_x2, \
                      body_coordinate_y2, \
                      body_w, \
                      body_h, \
                      body_angle, \
                      body_centroid_x, \
                      body_centroid_y
                  ]
    # trace("bodyInfo_data: {}".format(bodyInfo_data), _DEBUG)
    return bodyInfo_data

def extractOCVInfo(line:str):
    OCVInfo, OCVInfo_len = splitLineToList(line,";")
    OCV_data = OCVInfo[OCV.ocv_status.value]
    # trace("OCVInfo, OCVInfo_len:{} {}".format(OCVInfo, OCVInfo_len), _DEBUG)
    return OCV_data

def extractPinInfo(line:str):
    pinsInfo, pinsInfo_len = splitLineToList(line,";")
    pin_x1 = int(pinsInfo[Pin.coordinate_x1.value])
    pin_y1 = int(pinsInfo[Pin.coordinate_y1.value])
    pin_x2 = int(pinsInfo[Pin.coordinate_x2.value])
    pin_y2 = int(pinsInfo[Pin.coordinate_y2.value])
    pin_w = int(pinsInfo[Pin.pin_w.value])
    pin_h = int(pinsInfo[Pin.pin_h.value])
    
    pinsInfo_data = [ pin_x1, \
                      pin_y1, \
                      pin_x2, \
                      pin_y2, \
                      pin_w, \
                      pin_h \
                     ]
    # trace("pinsInfo_data: {}".format(pinsInfo_data), _DEBUG)
    return pinsInfo_data

def searchForPinInfo(line:str):
    info, info_len = splitLineToList(line,";")
    info_header = info[0]

    ocvInfo_data = None
    pinsInfo_data = None
    
    if("PIN" in info_header.upper() and info_len > 1):
        pinsInfo_data = extractPinInfo(line)
    else:
        print("[Warning]: Unrecognised header format. Header named `{}` appeared in the file.\n{}\n".format(info_header,line))
        
    return pinsInfo_data

def ExtractValueAtRefDes(refdes, info_df):
    for index, row in info_df.iterrows():
        if row['refDes'] == refdes:
            return row['type'], row['errMsg']
    
    raise ValueError("[Error: 404]: Refdes named {} is not found in result.rep file. \
    Please Check".format(refdes))            
# End: Extract DF functions -------------------------------------|



# Read and write functions --------------------------------------|
# /*************************************************************
#    Author          : JW
#    Description	 : While parsing the .tdev file use the
#    "view" line to group them into list and sublist.
#    Last Modified   : 
#    Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************/ 
def groupDataByView(lines: list):
    line_str_list = []
    line_str_list_all = []
    for index, line in enumerate(lines):
        line_str = line.decode("utf-8")
        
        if ("View") in line_str:
            if( line_str_list):
                line_str_list_all.append(line_str_list)
            line_str_list = []
        else:
            # Store the rest Info
            line_str_list.append(line_str)
            # trace(line_str, _DEBUG)
            
        if index == len(lines)-1:
            # line_str_list.append(line_str)
            line_str_list_all.append(line_str_list)
            line_str_list = []
    # return grouped data 
    return line_str_list_all

# /*************************************************************
#    Author          : JW
#    Description	 : Read rep file
#    Last Modified   : 
#    Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************/  
def ReadResultRepFile(rep_file_path, output_img_dir):
    try: 
        info_df = pd.read_csv(rep_file_path, skiprows=2, 
                              names=["refDes", "feeder", "type", \
                                     "pres", "angle","x", "y", \
                                     "theta", "errcode", "errMsg","Extra"],\
                                     sep = "\s+|\t+|\s+\t+|\t+\s+")
    except:
        print("ERROR: File: %s failed"%(f))
        sys.exit()
    
    output_file = os.path.join(output_img_dir,"output_rep.csv")
    info_df.to_csv(output_file)
    return info_df
    
def MergeTdevInfoIntoAllTileCSV(root_path, img_dir_pathlist, out_csv_dirpath):
    
    ##Path
    rep_file = os.path.join(os.path.dirname(out_csv_dirpath), "result.rep")
    output_dir = os.path.join(os.path.dirname(out_csv_dirpath))
    data_df = ReadResultRepFile(rep_file, output_dir)
    frames_list = []
    
    for img_dir_path in img_dir_pathlist:
        #print(img_dir_path)
        tile_name_dir = os.path.basename(img_dir_path)
        search_exp=os.path.join(root_path, img_dir_path)+ "/*.tdev"
        tdev_files_path = [f for f in glob.glob(search_exp, recursive=True)]
        
        TILE_CSV_PATH = os.path.join(out_csv_dirpath, tile_name_dir)
        if not os.path.exists(TILE_CSV_PATH):
            os.mkdir(TILE_CSV_PATH)
        
        for file in tdev_files_path:
            f = open(file,"rb")
            contents_list = []
            if f.mode == 'rb':
                contents = f.read()
                file_as_list = contents.splitlines()
            f.close()
            file_as_list = [x for x in file_as_list if x]
            allGroupedData_list = groupDataByView(file_as_list)

            # Metadata List - Used to generate Dataframe
            # Initialize all metadata list for every new file
            refDes_list = []
            componentType_list = []
            searchArea_list = []
            bodyArea_list = []
            ocv_list = []
            pins_list = []
            ocv_list = []
            rep_type_list = []
            err_message_list =  []
            path_list = []

            for group in allGroupedData_list:
                # Initialize all the metadata
                refdes_data = None
                package_data = None
                searchArea = None
                body_data = None
                ocv_data = None
                pin_data = None
                type_data = None
                err_data = None
                OCV_list = [] # temp list to store all the ocv search area
                Pins_list = [] # temp list to store all the pins search area

                for line_index, line in enumerate(group):    
                    if (line_index == 0):
                        refdes_data, package_data, searchArea_data = extractComponentInfo(line)
                    elif (line_index == 1):
                        body_data = extractBodyInfo(line)
                    elif (line_index == 2):
                        ocv_data = extractOCVInfo(line)
                    else:
                        # Rest are considered to be pins
                        pin_data = searchForPinInfo(line)
                        if(pin_data):
                            Pins_list.append(pin_data)
                    type_data, err_data = ExtractValueAtRefDes(refdes_data,  data_df)
                ## Using List for scaling in future, might used for combine multiple tile file, and make one
                ## .csv file
                #file_list.append()
                refDes_list.append(refdes_data)
                componentType_list.append(package_data)
                searchArea_list.append(searchArea_data)
                bodyArea_list.append(body_data)
                ocv_list.append(ocv_data)
                pins_list.append(Pins_list)
                rep_type_list.append(type_data)
                err_message_list.append(err_data)
                
                #Finding RGB file path
                full_img_dir_path=os.path.join(root_path, img_dir_path)
                jpg_paths = [f for f in glob.glob(full_img_dir_path + "/*.jpg", recursive=True)]
                tempappend = ""
                for jpgfile in jpg_paths:
                    if "RGB" in jpgfile:
                        tempappend = img_dir_path+"/"+os.path.basename(jpgfile)
                tempappend += "/"
                path_list.append(tempappend)
                

            info_df = pd.DataFrame({
                'path': path_list,
                'refDes': refDes_list,
                'package': componentType_list,
                'searchArea': searchArea_list,
                'body_dims': bodyArea_list,
                'ocv_dims': ocv_list,
                'pins_dims': pins_list,
                'pin_num': [len(item) for item in pins_list ],
                'type_rep': rep_type_list,
                'error': err_message_list
            })
            
            frames_list.append(info_df)

            output_file_csv = os.path.join(TILE_CSV_PATH,"processed_tile_{}.csv".format(tile_name_dir))
            output_file_text = os.path.join(TILE_CSV_PATH,"processed_tile_{}.txt".format(tile_name_dir))
            info_df.to_csv(output_file_csv, index=False)
            info_df.to_csv(output_file_text, index=False, header=None, sep=",")
            
    full_frame = pd.concat(frames_list)
    full_frame.to_csv(os.path.join(out_csv_dirpath, "all_tiles.csv"), index=False)
# End: Read and write functions ----------------------------------|
            


# /*************************************************************
#    Author          : Fazle
#    Description	 : Create a csv containing all the folling informations
#      'path': path_list,
#      'refDes': refDes_list,
#      'package': componentType_list,
#      'searchArea': searchArea_list,
#      'body_dims': bodyArea_list,
#      'ocv_dims': ocv_list,
#      'pins_dims': pins_list,
#      'pin_num': [len(item) for item in pins_list ],
#      'type_rep': rep_type_list,
#      'error': err_message_list#  
#    Last Modified   : 20190806_1342
#    Copyright © 2000, MV Technology Ltd. All rights reserved.
# *************************************************************/    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--tile_fpath", default=os.path.normpath("D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files/9611GCR2-T-7/Tiles"))
    parser.add_argument("--root_fpath", default=os.path.normpath("D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files"))
    parser.add_argument("--boardname", default="9611GCR2-T-7")
    parser.add_argument("--out_fpath", default=os.path.normpath("D:/FZ_WS/JyNB/Yolo_LD/tf_yolov3/LD_Files/9611GCR2-T-7"))
    flags = parser.parse_args()

    # Paths
    tile_dir_path = os.path.join(flags.root_fpath, flags.boardname, "Tiles")
    out_csv_dirpath = os.path.join(flags.out_fpath, "output")

    # Create
    if not os.path.exists(out_csv_dirpath):
        os.mkdir(out_csv_dirpath)

    img_dir_pathlist = [ os.path.join(flags.boardname, "Tiles", file) for file in os.listdir(tile_dir_path)\
        if not os.path.isfile( os.path.join(tile_dir_path, file))] 
    MergeTdevInfoIntoAllTileCSV(flags.root_fpath, img_dir_pathlist, out_csv_dirpath)