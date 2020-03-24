#! /usr/bin/env python
# coding=utf-8
#================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   Editor      : VIM
#   File name   : image_demo.py
#   Author      : YunYang1994
#   Created date: 2019-01-20 16:06:06
#   Description :
#
#================================================================

import cv2
import datetime, os
import numpy as np
import core.utils as utils
import tensorflow as tf
from PIL import Image

return_elements = ["input/input_data:0", "pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"]
pb_file         = "./yolov3_ld_00.pb"
image_path      = "D:/FZ_WS/JyNB/Yolo_LD/Tf_Yolov3/dataset/LD_Dataset_01_RGB/train/73-12012-22_A0_TOP_JMX_90_180_d18.jpg"
num_classes     = 2 #80
input_size      = 608
graph           = tf.Graph()

original_image = cv2.imread(image_path)
original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
original_image_size = original_image.shape[:2]

# Preprocess
# image_data = utils.image_preporcess(np.copy(original_image), [input_size, input_size])
image_data = utils.ObjectDetectionUtility.getInstance().image_preporcess(np.copy(original_image), [input_size, input_size])


image_data = image_data[np.newaxis, ...]
return_tensors = utils.read_pb_return_tensors(graph, pb_file, return_elements)


with tf.Session(graph=graph) as sess:
    pred_sbbox, pred_mbbox, pred_lbbox = sess.run(
        [return_tensors[1], return_tensors[2], return_tensors[3]],
                feed_dict={ return_tensors[0]: image_data})

pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + num_classes)),
                            np.reshape(pred_mbbox, (-1, 5 + num_classes)),
                            np.reshape(pred_lbbox, (-1, 5 + num_classes))], axis=0)

bboxes = utils.postprocess_boxes(pred_bbox, original_image_size, input_size, 0.3)
bboxes = utils.nms(bboxes, 0.45, method='nms')
image = utils.draw_bbox(original_image, bboxes)
name= os.path.join ("./data/userlog/Image_Demo-" , str(datetime.datetime.now()).replace(".","_").replace(":","_").replace(" ","_") +".jpg")
cv2.imwrite(name,image)

image = Image.fromarray(image)
image.show()




