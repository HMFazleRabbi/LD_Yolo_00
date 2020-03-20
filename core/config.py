#! /usr/bin/env python
# coding=utf-8
#================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   Editor      : VIM
#   File name   : config.py
#   Author      : YunYang1994
#   Created date: 2019-02-28 13:06:54
#   Description :
#
#================================================================

from easydict import EasyDict as edict


__C                             = edict()
# Consumers can get config by: from config import cfg

cfg                             = __C

# YOLO options
__C.YOLO                        = edict()

# Set the class name
__C.YOLO.CHANNELS               = 3 
__C.YOLO.CLASSES                = "./data/classes/lead_detector.names"
__C.YOLO.ANCHORS                = "./data/anchors/basline_anchors.txt"
__C.YOLO.MOVING_AVE_DECAY       = 0.9995 
__C.YOLO.STRIDES                = [8, 16, 32]
__C.YOLO.ANCHOR_PER_SCALE       = 3
__C.YOLO.IOU_LOSS_THRESH        = 0.5
__C.YOLO.UPSAMPLE_METHOD        = "resize"
__C.YOLO.ORIGINAL_WEIGHT        = "./checkpoint/Pretrained_weights/yolov3_coco.ckpt"
__C.YOLO.DEMO_WEIGHT            = "./checkpoint/Pretrained_weights/Yolov3_Coco_Pretrained.ckpt"

# Train options
__C.TRAIN                       = edict()
__C.TRAIN.ANNOT_PATH            = "./dataset/LD_Dataset_01_RGB/train"
__C.TRAIN.BATCH_SIZE            = 8 
__C.TRAIN.INPUT_SIZE            = [608] # [320, 352, 384, 416, 448, 480, 512, 544, 576, 608]
__C.TRAIN.SMALLSCALE_INPUT_SIZE = [208,224,240,256,272,288,304,320,336,352,368,384,400,416,432,448,464,480,496] 
__C.TRAIN.LARGESCALE_INPUT_SIZE = [512, 528, 544, 560, 576, 592, 608]
__C.TRAIN.DATA_AUG              = True
__C.TRAIN.LEARN_RATE_INIT       = 1e-3  #1e-4
__C.TRAIN.LEARN_RATE_END        = 1e-6
__C.TRAIN.WARMUP_EPOCHS         = 2     #2
__C.TRAIN.FISRT_STAGE_EPOCHS    = 20    #20
__C.TRAIN.SECOND_STAGE_EPOCHS   = 500   #30
__C.TRAIN.INITIAL_WEIGHT        = "./checkpoint/Pretrained_weights/Yolov3_Coco_Pretrained.ckpt" 



# TEST options
__C.TEST                        = edict()
__C.TEST.ANNOT_PATH             = "./dataset/LD_Dataset_01_RGB/test" 
__C.TEST.BATCH_SIZE             = 1 #2
__C.TEST.INPUT_SIZE             = 544
__C.TEST.DATA_AUG               = False
__C.TEST.WRITE_IMAGE            = True
__C.TEST.WRITE_IMAGE_PATH       = "./data/detection"
__C.TEST.WRITE_IMAGE_SHOW_LABEL = True
__C.TEST.WEIGHT_FILE            = "./checkpoint/ActiveCheckpoint/yolov3_test_loss=169.9338.ckpt-17"
__C.TEST.SHOW_LABEL             = True
__C.TEST.SCORE_THRESHOLD        = 0.75
__C.TEST.IOU_THRESHOLD          = 0.45

