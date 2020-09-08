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
__C.YOLO.CLASSES                = "./data/classes/pad.names"
__C.YOLO.ANCHORS                = "./data/anchors/basline_anchors.txt"
__C.YOLO.MOVING_AVE_DECAY       = 0.9995
__C.YOLO.STRIDES                = [8, 16, 32]
__C.YOLO.ANCHOR_PER_SCALE       = 3
__C.YOLO.IOU_LOSS_THRESH        = 0.5
__C.YOLO.UPSAMPLE_METHOD        = "resize"
__C.YOLO.ORIGINAL_WEIGHT        = "./checkpoint/Pretrained_Weight/yolov3_coco.ckpt"
__C.YOLO.DEMO_WEIGHT            = "./checkpoint/Pretrained_Weight/yolov3_coco_pretrained.ckpt"

# Train options
__C.TRAIN                       = edict()

__C.TRAIN.ANNOT_PATH            = "./data/dataset/Exp-08/train.txt"
__C.TRAIN.BATCH_SIZE            = 2
__C.TRAIN.INPUT_SIZE            = [928,960,992,1024,1056,1088]
__C.TRAIN.DATA_AUG              = True
__C.TRAIN.LEARN_RATE_INIT       = 1e-4
__C.TRAIN.LEARN_RATE_END        = 1e-6
__C.TRAIN.WARMUP_EPOCHS         = 10
__C.TRAIN.FISRT_STAGE_EPOCHS    = 50
__C.TRAIN.SECOND_STAGE_EPOCHS   = 50
__C.TRAIN.INITIAL_WEIGHT        = "./checkpoint/Exp-8-A-01/Exp-8-A-01_test_loss=169.7120.ckpt-20" 
__C.TRAIN.LOGDIR                = "./data/log/Exp-8-A-08"
__C.TRAIN.OUTPUT_WEIGHT         = "./checkpoint/Exp-8-A-08"



# TEST options
__C.TEST                        = edict()

__C.TEST.ANNOT_PATH             = "./data/dataset/Exp-08/test.txt"
__C.TEST.BATCH_SIZE             = 1
__C.TEST.INPUT_SIZE             = 1024
__C.TEST.DATA_AUG               = False
__C.TEST.WRITE_IMAGE            = True
__C.TEST.WRITE_IMAGE_PATH       = "./data/detection/Exp-8-A-08/test/"
__C.TEST.WRITE_IMAGE_SHOW_LABEL = False
__C.TEST.WEIGHT_FILE            = "./checkpoint/Exp-8-A-08/Exp-8-A-03_test_loss=14.0184.ckpt-28"
__C.TEST.SHOW_LABEL             = False
__C.TEST.SCORE_THRESHOLD        = 0.60
__C.TEST.IOU_THRESHOLD          = 0.45

