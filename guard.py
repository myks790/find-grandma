import os
import time
import cv2
import numpy as np
from threading import Thread
from multiprocessing import Process, Queue
from yolo3_one_file_to_detect_them_all import make_yolov3_model, preprocess_input, decode_netout, correct_yolo_boxes, \
    do_nms, draw_boxes, labels, anchors, WeightReader

snapshots_folder = '/snapshots/'
result_folder = '/result/'
pre_folder = '/pre/'


def predict_save(base_path, file_name, yolov3):
    save_path = base_path + result_folder
    move_path = base_path + pre_folder
    image_file_path = base_path + snapshots_folder + file_name
    move_file_path = move_path + file_name
    save_file_path = save_path + file_name[:-4] + '_detected' + file_name[-4:]

    if os.path.isfile(save_file_path):
        if os.path.isfile(image_file_path):
            os.rename(image_file_path, move_file_path)
        return

    # set some parameters
    net_h, net_w = 416, 416
    obj_thresh, nms_thresh = 0.505, 0.45
    # preprocess the image
    image = cv2.imread(image_file_path)
    image_h, image_w, _ = image.shape
    new_image = preprocess_input(image, net_h, net_w)

    # run the prediction
    yolos = yolov3.predict(new_image)

    boxes = []

    for i in range(len(yolos)):
        # decode the output of the network
        boxes += decode_netout(yolos[i][0], anchors[i], obj_thresh, nms_thresh, net_h, net_w)

    # correct the sizes of the bounding boxes
    correct_yolo_boxes(boxes, image_h, image_w, net_h, net_w)

    # suppress non-maximal boxes
    do_nms(boxes, nms_thresh)

    # draw bounding boxes on the image using labels
    result = draw_boxes(image, boxes, labels, obj_thresh)
    # print('image_path :', image_path, '  ', result)
    remove_flag = True
    for e in result:
        if e['label'] == 'person':
            # write the image with bounding boxes to file
            remove_flag = False
            cv2.imwrite(save_file_path, (image).astype('uint8'))
            os.rename(image_file_path, move_file_path)
            break
    if remove_flag:
        os.remove(image_file_path)
        # print('remove : image_path : ', image_path)


def process(base_path, file_queue, weights_path):
    # make the yolov3 model to predict 80 classes on COCO
    yolov3 = make_yolov3_model()

    # load the weights trained on COCO into the model
    weight_reader = WeightReader(weights_path)
    weight_reader.load_weights(yolov3)

    while True:
        try:
            predict_save(base_path, file_queue.get(), yolov3)
        except PermissionError:
            print(PermissionError)
            time.sleep(10)
            predict_save(base_path, file_queue.get(), yolov3)


def mse(img_a, img_b):
    err = np.sum((img_a.astype('float') - img_b.astype('float')) ** 2)
    err /= float(img_a.shape[0] * img_a.shape[1])
    return err


def load_file(base_path, file_queue):
    print('load... file path: ', base_path)
    path = base_path + snapshots_folder
    pre_path = base_path + pre_folder
    file_list = os.listdir(path)
    last_file_name = ''

    while True:
        target_files = []
        for file_name in file_list:
            if file_list[len(file_list) - 1] == file_name:
                break
            if file_name > last_file_name:
                if os.path.isfile(pre_path + last_file_name):
                    crop_rast_img = cv2.imread(pre_path + last_file_name)
                else:
                    crop_rast_img = cv2.imread(path + last_file_name)
                crop_img = cv2.imread(path + file_name)
                if crop_rast_img is not None and mse(crop_rast_img, crop_img) < 100:
                    try:
                        os.remove(path + file_name)
                    except PermissionError:
                        time.sleep(10)
                        os.remove(path + file_name)
                else:
                    target_files.append(file_name)
                    last_file_name = file_name
        for file_name in target_files:
            file_queue.put(file_name)
        file_list = os.listdir(path)
        time.sleep(10)


def watch(base_path, weights_path):
    file_queue = Queue(50)
    t = Thread(target=load_file, args=(base_path, file_queue,))
    t.daemon = True
    t.start()

    ps = []
    for _ in range(7):
        ps.append(Process(target=process, args=(base_path, file_queue, weights_path,)))
    for p in ps:
        p.start()
    for p in ps:
        p.join()
