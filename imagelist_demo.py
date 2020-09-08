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

import cv2, os
import glob as glob
import numpy as np
import core.utils as utils
import tensorflow as tf
from PIL import Image

def main():

    # User defined Parameters
    in_img_dir      = "F:/new_board/all"
    out_img_dir     = "F:/new_board/Exp-8-A-04_test_loss=13.9570.ckpt-46-30percent"
    pb_file         = "D:/FZ_WS/JyNB/Yolo_Pad_WS/Yolo_Pad_00/checkpoint/Exp-4-0/Exp-8-A-04_test_loss=13.9570.ckpt-46.pb" 
    return_elements = ["input/input_data:0", "pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"]
    num_classes     = 1
    input_size      = 1024
    score_threshold = 0.3
    nms_threshold   = 0.45


    #Variables
    graph           = tf.Graph()
    return_tensors = utils.read_pb_return_tensors(graph, pb_file, return_elements)

    # Session
    with tf.Session(graph=graph) as sess:
        img_list=glob.glob(in_img_dir+"/*.jpg")
        
        for image_path in img_list:
            print(image_path)
            original_image = cv2.imread(image_path, cv2.IMREAD_COLOR)
            # original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            original_image_size = original_image.shape[:2]
            image_data = utils.image_preporcess(np.copy(original_image), [input_size, input_size])
            image_data = image_data[np.newaxis, ...]


            # Prediction
            pred_sbbox, pred_mbbox, pred_lbbox = sess.run(
                [return_tensors[1], return_tensors[2], return_tensors[3]],
                        feed_dict={ return_tensors[0]: image_data})

            # Post processing
            pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + num_classes)),
                                        np.reshape(pred_mbbox, (-1, 5 + num_classes)),
                                        np.reshape(pred_lbbox, (-1, 5 + num_classes))], axis=0)

            bboxes = utils.postprocess_boxes(pred_bbox, original_image_size, input_size, score_threshold)
            bboxes = utils.nms(bboxes, nms_threshold, method='nms')

            # Output
            image = utils.draw_bbox(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB), bboxes, show_label=False)
            image = Image.fromarray(image)
            image.save(os.path.join(out_img_dir, os.path.basename(image_path)))
            

if __name__ == "__main__":
    main()
    pass



