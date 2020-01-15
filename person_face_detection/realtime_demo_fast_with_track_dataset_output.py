# -*- coding: UTF-8 -*-
import cv2
import os
from time import sleep
import numpy as np
import argparse
from wide_resnet import WideResNet
import time
from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from deep_sort.detection import Detection as ddet
import pickle
import height_estimation
import goldfishdb
from detector import detect_faces
from PIL import Image
import pedestrian_wide_resnet
import pedestrian_wide_resnet_age

LOCAL_DIR = "/Users/Sanny02/Downloads/Goldfish_backend 2"

class Goldfish(object):
    """
    Singleton class for face recongnition task
    """

    CASE_PATH = LOCAL_DIR + "/pretrained_models/haarcascade_frontalface_alt.xml"
    WRN_WEIGHTS_PATH = LOCAL_DIR + "/pretrained_models/weights.18-4.06.hdf5"
    BODY_AGE_WEIGHTS_PATH = LOCAL_DIR + "/pretrained_models/body_age_3.hdf5"
    BODY_GENDER_WEIGHTS_PATH = LOCAL_DIR + "/pretrained_models/body_gender.hdf5"

    PROTO = LOCAL_DIR + "/pretrained_models/deploy.prototxt"
    MOBILE_CAFFE = LOCAL_DIR + "/pretrained_models/mobilenet_iter_73000.caffemodel"
    COLORS = (0, 255, 0)
    TRACK_COLORS = (255, 255, 255)
    CONFIDENCE_THRESHOLD = 0.2
    PEDESTRIAN_YOLO = LOCAL_DIR + '/model_data/mars-small128.pb'

    #VIDEO = '/Users/michelle/Documents/cut.mp4'
    # VIDEO = 0
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
               "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
               "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
               "sofa", "train", "tvmonitor"]
    PER_FRAME = 25
    MAX_COSINE_DISTANCE = 0.3
    NN_BUDGET = None
    NMS_MAX_OVERLAP = 1.0
    SCORE = 0.5
    IOU = 0.5
    HEIGHT_PARAMETERS = LOCAL_DIR +'/model_data/parameters.pkl'

    def __new__(cls, video_dir,weight_file=None, depth=16, width=8, face_size=64):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Goldfish, cls).__new__(cls)
        return cls.instance

    def __init__(self, video_dir, depth=16, width=8, face_size=64):
        self.face_size = face_size
        self.VIDEO = video_dir
        self.ag_model = WideResNet(face_size, depth=depth, k=width)()
        #model_dir = os.path.join(os.getcwd(), "pretrained_models").replace("//", "\\")
        #fpath = get_file('weights.18-4.06.hdf5',
        #                 self.WRN_WEIGHTS_PATH,
        #                 cache_subdir=model_dir)
        self.ag_model.load_weights(self.WRN_WEIGHTS_PATH)

        self.body_age_model = pedestrian_wide_resnet_age.WideResNet(128, 128, depth=16, k=2)()
        self.body_age_model.load_weights(self.BODY_AGE_WEIGHTS_PATH)
        self.body_gender_model = pedestrian_wide_resnet.WideResNet(128, 128, depth=22, k=1)()
        self.body_gender_model.load_weights(self.BODY_GENDER_WEIGHTS_PATH)

        self.pedestrian_model = cv2.dnn.readNetFromCaffe(self.PROTO, self.MOBILE_CAFFE)
        self.face_cascade = cv2.CascadeClassifier(self.CASE_PATH)
        self.pedestrian_model_input_encoder = gdet.create_box_encoder(self.PEDESTRIAN_YOLO, batch_size=1)
        self.metric = nn_matching.NearestNeighborDistanceMetric('cosine', self.MAX_COSINE_DISTANCE, self.NN_BUDGET)
        self.pedestrian_tracker = Tracker(self.metric)
        self.height_estimation_param = pickle.load(open(self.HEIGHT_PARAMETERS, 'rb'), encoding='iso-8859-1')

    @classmethod
    def draw_label(cls, image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
                   font_scale=1, thickness=2):
        size = cv2.getTextSize(label, font, font_scale, thickness)[0]
        x, y = point
        cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
        cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness)

    def crop_face(self, imgarray, section, margin=40, size=64):
        """
        :param imgarray: full image
        :param section: face detected area (x, y, w, h)
        :param margin: add some margin to the face detected area to include a full head
        :param size: the result image resolution with be (size x size)
        :return: resized image in numpy array with shape (size x size x 3)
        """
        img_h, img_w, _ = imgarray.shape
        # print("img_h={},img_w={}".format(img_h,img_w))
        if section is None:
            section = [0, 0, img_w, img_h]
        (x1, y1, x2, y2, _) = section
        # print(x1,y1,x2,y2)
        margin = int(min((x2 - x1), (y2 - y1)) * margin / 100)
        # print(margin)
        x_a = int(x1 - margin)
        y_a = int(y1 - margin)
        x_b = int(x2 + margin)
        y_b = int(y2 + margin)
        if x_a < 0:
            x_a = 0
        if y_a < 0:
            y_a = 0
        if x_b > img_w:
            x_b = img_w
        if y_b > img_h:
            y_b = img_h
        # print(x_a, y_a, x_b, y_b),
        # print('face')
        cropped = imgarray[y_a: y_b, x_a: x_b]
        resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
        resized_img = np.array(resized_img)
        return resized_img, (x_a, y_a, x_b, y_b)

    def crop_person(self, imgarray, section, margin=0, size=64):
        """
        :param imgarray: full image
        :param section: person detected area (x1, y1, x2, y2)

        """
        img_h, img_w, _ = imgarray.shape
        if section is None:
            section = [0, 0, img_w, img_h]
        # (x1, y1, x2, y2) = section
        # margin = int(min(w, h) * margin / 100)
        # (x_l, y_l, x_r, y_h) = (section * np.array([img_w, img_h, img_w, img_h])).astype('int')

        (x_l, y_l, x_r, y_h) = np.asarray(section).astype('int')
        if x_l > x_r:
            x_l, x_r = x_r, x_l
        if y_l > y_h:
            y_l, y_h = y_h, y_l

        margin = int(min(x_r - x_l, y_h - y_l) * margin / 100)

        # print(margin)
        x_l = x_l - margin
        y_l = y_l - margin
        y_h = y_h + margin
        x_r = x_r + margin

        if x_l < 0:
            x_r = min(x_r - x_l, img_w - 1)
            x_l = 0
        if y_l < 0:
            y_h = min(y_h - y_l, img_h - 1)
            y_l = 0
        if x_r >= img_w:
            x_l = max(x_l - (x_r - img_w), 0)
            x_r = img_w - 1
        if y_h >= img_h:
            y_l = max(y_l - (y_h - img_h), 0)
            y_h = img_h - 1

        # y_l = y_l if y_l >= 0 else 0
        # x_l = x_l if x_l >= 0 else 0
        # x_r = x_r if x_r <= img_w else img_w
        # y_h = y_h if y_h <= img_h else img_h
        cropped = imgarray[y_l: y_h, x_l: x_r]
        # resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
        # resized_img = np.array(resized_img)
        return cropped

    def to_xlwh(self, sections):
        # return x, y, w, h
        ret = sections.copy()
        ret[:, 2:] -= ret[:, :2]
        return ret

    def create_new_person_data(self, val, current_time, section, height_val, score):
        new_person_data = {}
        new_person_data['PID'] = val
        new_person_data['Time'] = current_time
        new_person_data['Score'] = score
        new_person_data['Gender'] = -1
        new_person_data['Age'] = -1
        new_person_data['Height'] = height_val
        new_person_data['x1'] = section[0]
        new_person_data['y1'] = section[1]
        new_person_data['x2'] = section[2]
        new_person_data['y2'] = section[3]
        return new_person_data

    def detect_pedestrian(self):
        video_capture = cv2.VideoCapture(self.VIDEO)
        #fourcc = cv2.VideoWriter_fourcc(*'MP42')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        # fps = video_capture.get(5)
        size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        #video_output = cv2.VideoWriter(self.VIDEO.split('.')[0] + '_out_test_new.mp4',
        print ("video_output",self.VIDEO)
        video_output = cv2.VideoWriter(os.path.join(LOCAL_DIR, self.VIDEO.split('/')[-1]),
                                       fourcc,
                                       fps, size)
        #video_output = cv2.VideoWriter('/Users/michelle/Documents/research/goldfish/static/'+ self.VIDEO.split('/')[-1]
        #                               , 0x00000021, 15.0, (1280, 360))
        dataset_output_list = []
        # person1
        #  'PID': 1 , 'Start_Time': 2.003, 'End_Time': 4.0009,
        #  'x1': 0, 'y1':10, 'x2':4, 'y2':20,
        #  'Gender': 1, 'Age': 20, 'Height': 180

        # for person in detection:
        #    tmp = {'PID': -1, 'Start_Time': 0.0, 'End_Time': 0.0,
        #  'x1': 0, 'y1':0, 'x2':0, 'y2':0,
        #  'Gender': -1, 'Age': -1, 'Height': -1}
        #    tmp['PID'] = 1

        frame_index = -1
        height_dic = {}
        body_age_check = ['Teenager', 'Youth', 'Middle Age', 'About 60', 'Ageing']
        body_age_check_int = {'Teenager': 15, 'Youth': 23, 'Middle Age': 35, 'About 60': 60, 'Ageing': 70}
        while True:
            if not video_capture.isOpened():
                sleep(5)
            tic = time.time()
            ret, frame = video_capture.read()
            if not ret:
                break
            origin_frame = frame.copy()
            frame_index += 1
            # todo get frame of per second ??? get more quicker computation of one video
            # if frame_index % fps is not 0:
            #     continue

            # time of this frame in the video
            current_time = video_capture.get(0)

            (height, width) = frame.shape[:2]
            # blob images by resizing images to a fixed 300*300 pixels and bath normalized
            blob_images = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, size=(300, 300), mean=127.5)
            # print("Computing Pedestrian Detection...")
            self.pedestrian_model.setInput(blob_images)
            objects = self.pedestrian_model.forward()
            objects = objects[0, 0, :]

            pedestrians = np.asarray([obs for obs in objects if int(obs[1]) == self.CLASSES.index('person')
                                      and obs[2] > self.CONFIDENCE_THRESHOLD])

            tracked_pedestrians = []
            tracked_confidence_list = []
            tracked_this_frame_id_list = []
            height_list = []
            all_whole_bodys = []

            track_id_list = []
            faces = []
            whole_bodys = []
            full_detected_persons = []

            non_track_id_list = []
            non_face_whole_bodys = []
            non_face_full_detected_persons = []


            if len(pedestrians) > 0:
                # print(pedestrians)
                pedestrians_to_track = pedestrians[:, 3:]

                boxes = self.to_xlwh(pedestrians_to_track * np.array([width, height, width, height]))

                # extract img of persons in the whole frame
                features = self.pedestrian_model_input_encoder(frame, boxes)

                detections = [Detection(box, detected_pedestrian[2], feature) for box, feature, detected_pedestrian in
                              zip(boxes, features, pedestrians)]

                # Return non-maxima suppression and modify detections
                boxes_array = np.array([d.tlwh for d in detections])
                scores = np.array([d.confidence for d in detections])

                # TODO ??? already have NMS in MobileNet Output layer
                indices = preprocessing.non_max_suppression(boxes_array, self.NMS_MAX_OVERLAP, scores)
                detections = [detections[i] for i in indices]

                # related to last frame
                self.pedestrian_tracker.predict()
                # find in this frame
                self.pedestrian_tracker.update(detections)

                # person tracked in the tracker to count person and generate more referable information from this system
                if len(pedestrians) > len(self.pedestrian_tracker.tracks):
                    print('!!!!LOST SOME PERSON DETECTIONS!!!')
                # print("tracks:%d" % len(self.pedestrian_tracker.tracks))
                for track in self.pedestrian_tracker.tracks:
                    if not track.is_confirmed() or track.time_since_update > 1:
                        continue
                    # return min_x, min_y, max_x, max_y
                    bbox = track.to_tlbr()
                    min_x, min_y, max_x, max_y = bbox
                    # print(min_x, min_y, max_x, max_y)
                    tracked_pedestrians.append(bbox)
                    tracked_confidence_list.append(track.confidence)
                    # PID of each person in the video
                    person_id = track.track_id
                    tracked_this_frame_id_list.append(track.track_id)
                    # todo get occurrence time of this person in this video
                    # track.age : int total number of frames since first occurance.
                    # if track.track_id => has_value?
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255), 2)
                    #cv2.putText(frame, str(track.track_id), (int(bbox[0]), int(bbox[1])), 0, 5e-3 * 200, (0, 255, 0), 2)
                    cv2.putText(frame, str(track.track_id), (int(bbox[2]), int(bbox[3])), 2, 5e-3 * 200, (0, 140, 255),
                                2)
                tracked_pedestrians = np.asarray(tracked_pedestrians)

                # print("Finding Face...")

                # todo if no faces detected in one pedestrian
                if len(self.pedestrian_tracker.tracks) > 0:
                    body_imgs = np.empty((tracked_pedestrians.shape[0], 128, 128, 3))
                    i = 0
                    for pedestrian_dectection in self.pedestrian_tracker.tracks:
                        if not pedestrian_dectection.is_confirmed() or pedestrian_dectection.time_since_update > 1:
                            continue
                        whole_body = self.crop_person(origin_frame, pedestrian_dectection.to_tlbr())
                        img = Image.fromarray(whole_body)
                        img = img.convert('RGB')
                        resized_img = cv2.resize(whole_body, (128, 128), interpolation=cv2.INTER_AREA)
                        resized_img = np.array(resized_img)
                        body_imgs[i, :, :, :] = resized_img
                        i += 1
                        if person_id not in height_dic.keys():
                            resized_img = cv2.resize(whole_body, (200, 400), interpolation=cv2.INTER_AREA)
                            cv2.imwrite("./model_data/person_pic/%s.jpg" % person_id, resized_img)
                            # cv2.imwrite("/Users/michelle/Documents/research/goldfish/static/images/%s.jpg" % person_id, resized_img)

                        try:
                            bounding_boxes, _ = detect_faces(img)
                            if len(bounding_boxes) == 1 and (
                                    bounding_boxes[0][2] > img.size[0] or bounding_boxes[0][3] > img.size[1]):
                                raise ValueError
                            if len(bounding_boxes) == 1:
                                print("bounding_boxes",bounding_boxes)
                                track_id_list.append(pedestrian_dectection.track_id)
                                whole_bodys.append(whole_body)
                                faces.extend(bounding_boxes)
                                full_detected_persons.append(
                                    pedestrian_dectection.to_tlbr())
                            else:
                                non_track_id_list.append(pedestrian_dectection.track_id)
                                non_face_whole_bodys.append(whole_body)
                                non_face_full_detected_persons.append(
                                    pedestrian_dectection.to_tlbr())
                            # print(bounding_boxes)
                        except Exception as e:
                            print(e)
                    """        
                    if len(body_imgs) > 0:
                        # all_whole_bodys = np.asarray(all_whole_bodys).reshape((-1, 128, 128, 3))
                        body_age_results = self.body_age_model.predict(body_imgs)
                        print(body_age_results)
                        body_gender_results = self.body_gender_model.predict(body_imgs)
                        body_ages = np.arange(0, 5).reshape(5, 1)
                        body_predicted_ages = body_age_results.dot(body_ages).flatten()
                        print(body_predicted_ages)
                        for idx, coordinates in enumerate(tracked_pedestrians):
                            this_body_gender = 'Female' if body_gender_results[idx][0] > 0.5 else 'Male'
                            cv2.putText(frame, body_age_check[int(body_predicted_ages[idx])] + ' ' + this_body_gender,
                                        (int(coordinates[0]), int(coordinates[1])), 1, 5e-3 * 200,
                                        (255, 255, 255), 2)
                    """



                # print("tracks:%d"%len(self.pedestrian_tracker.tracks))
                # print("faces:%d"%len(faces))
                # placeholder for cropped faces
                face_imgs = np.empty((len(faces), self.face_size, self.face_size, 3))
                cropped_all = []
                for i, face in enumerate(faces):
                    # print(face)
                    face_img, cropped = self.crop_face(whole_bodys[i], face, margin=20, size=self.face_size)
                    # TODO alignment
                    (x1, y1, x2, y2) = cropped
                    cropped_all.append([int(x1 + full_detected_persons[i][0]), int(y1 + full_detected_persons[i][1]),
                                        int(x2 + full_detected_persons[i][0]), int(y2 + full_detected_persons[i][1])])

                    cv2.rectangle(frame, (int(x1 + full_detected_persons[i][0]), int(y1 + full_detected_persons[i][1])),
                                  (int(x2 + full_detected_persons[i][0]), int(y2 + full_detected_persons[i][1])),
                                  (255, 200, 0), 2)
                    face_imgs[i, :, :, :] = face_img
                if len(face_imgs) > 0:
                    # predict ages and genders of the detected faces
                    results = self.ag_model.predict(face_imgs)
                    predicted_genders = results[0]
                    ages = np.arange(0, 101).reshape(101, 1)
                    predicted_ages = results[1].dot(ages).flatten()
                # draw results
                label_faces = []
                for i, face in enumerate(faces):
                    label = "{}, {}".format(int(predicted_ages[i]),
                                            "Female" if predicted_genders[i][0] > 0.5 else "Male")
                    label_faces.append(label.split(',')[1])
                    self.draw_label(frame,
                                    (int(face[0]) + int(full_detected_persons[i][0]),
                                     int(face[1]) + int(full_detected_persons[i][1])),
                                    label)
                if len(body_imgs) > 0:
                    # body_age_results = self.body_age_model.predict(body_imgs)
                    body_age_results = self.body_age_model.predict(body_imgs / 255.)
                    body_gender_results = self.body_gender_model.predict(body_imgs)
                    body_ages = np.arange(0, 5).reshape(5, 1)
                    body_predicted_ages = body_age_results.dot(body_ages).flatten()
                    for idx, coordinates in enumerate(tracked_pedestrians):
                        this_body_gender = 'Female' if body_gender_results[idx][0] > 1e-5 else 'Male'
                        for idx, crop in enumerate(cropped_all):
                            x1, y1, x2, y2 = crop
                            if (coordinates[0] <= x1 and \
                                    coordinates[1] <= y1 and coordinates[2] >= x2 and \
                                    coordinates[3] >= y2):
                                this_body_gender = label_faces[idx]
                                break
                        cv2.putText(frame, body_age_check[int(body_predicted_ages[idx])] + ' ' + this_body_gender,
                                    (int(coordinates[0]), int(coordinates[1] - 5)), 1, 5e-3 * 200,
                                    (255, 255, 255), 2)
                for person in pedestrians:
                    confidence = person[2]

                    # bounding box real coordinate
                    box = person[3:] * np.array([width, height, width, height])
                    (x1, y1, x2, y2) = box.astype('int')
                    # probabiltiy of person
                    # label = "人: %.2f%%"%(confidence * 1.0)
                    label = "Person: %.2f%%" % (confidence * 100.0)

                    # draw a box
                    # cv2.putText(framecv2.rectangle(frame, (x1, y1), (x2, y2), self.COLORS, 2)

                if tracked_pedestrians.size > 0:
                    # get x, y coordinate of every person in this frame

                    reference_plane_scale = 0.2

                    height_scale = 0.2

                    for track_id, person in enumerate(tracked_pedestrians):
                        # confidence = person[2]
                        box = person

                        (x1, y1, x2, y2) = box.astype('int')
                        # probabiltiy of person
                        # label = "人: %.2f%%"%(confidence * 1.0)
                        label = "Person: %.2f%%" % (tracked_confidence_list[track_id] * 100)

                        # draw a box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), self.TRACK_COLORS, 2)

                        # add label text on the box
                        y = y1 - 15 if y1 - 15 > 15 else y1 + 15
                        # cv2.putText(frame, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.TRACK_COLORS, 2)

                        middle_x = int(1.0 * (x1 + x2) / 2)
                        height_person = height_estimation.height_estimate((middle_x, y1), (middle_x, y2),
                                                                          self.height_estimation_param)
                        height_label = '%.2f m' % (height_person)
                        pid = tracked_this_frame_id_list[track_id]
                        if 1.5 < height_person < 1.9:
                            if pid not in height_dic.keys():
                                height_dic[pid] = [height_person]
                            else:
                                height_dic[pid].append(height_person)
                            height_label = '%.2f m' % (height_person)
                        else:
                            if pid not in height_dic.keys():
                                height_dic[pid] = [height_person]
                                height_label = 'Abnormal Estimation,May contain more than 1 people'
                                height_person = 1.7
                            else:
                                height_person = sum(height_dic[pid]) / len(height_dic[pid])
                                height_label = '%.2f m' % (height_person)
                                if height_person > 1.9 or height_person < 1.5:
                                    height_label = 'Abnormal Estimation,May contain more than 1 people'
                                    height_person = 1.7
                        # height_label = '%.2f m' % (height_person)
                        cv2.putText(frame, height_label, (x1, y1 - 20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (211, 211, 211), 2)
                        height_list.append(height_person)
                    '''
                    data:
                ===tracked with detected face and age and gender====
                track_id_list = []
                faces = []
                whole_bodys = []
                full_detected_persons = []
                predicted_genders = results[0]
                predicted_ages = results[1].dot(ages).flatten()

                ===tracked without detected face and age and gender====
                non_track_id_list = []
                non_face_whole_bodys = []
                non_face_full_detected_persons = []
                
                ===total tracked list===
                tracked_pedestrians = []
                tracked_this_frame_id_list = []
                height_list = []
                
                    '''

            # person1
            #  'PID': 1 , 'Time': 2.003,
            #  'x1': 0, 'y1':10, 'x2':4, 'y2':20,
            #  'Gender': 1, 'Age': 20, 'Height': 180

            # for person in detection:
            #    tmp = {'PID': -1, 'Start_Time': 0.0, 'End_Time': 0.0,
            #  'x1': 0, 'y1':0, 'x2':0, 'y2':0,
            #  'Gender': -1, 'Age': -1, 'Height': -1}

            # dataset_output_list
            if len(tracked_this_frame_id_list) > 0:
                for idx, val in enumerate(tracked_this_frame_id_list):
                    new_person_data = self.create_new_person_data(val, current_time / 1000,
                                                                  tracked_pedestrians[idx], height_list[idx],
                                                                  tracked_confidence_list[idx])
                    if val in track_id_list:
                        face_idx = track_id_list.index(val)
                        new_person_data['Age'] = predicted_ages[face_idx]
                        new_person_data['Gender'] = int(predicted_genders[face_idx][0])
                    else:
                        new_person_data['Age'] = body_age_check_int[body_age_check[int(body_predicted_ages[idx])]]
                        new_person_data['Gender'] = int(body_gender_results[idx][0])
                    dataset_output_list.append(new_person_data)

            toc = time.time()
            durr = float(toc - tic)
            print_fps = 1.0 / durr
            cv2.putText(frame, "fps: %.3f" % print_fps, (20, 20), 2, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Current Time: %.3f sec" % (current_time / 1000), (int(width * 0.65), 20), 2, 0.8,
                        (0, 0, 255), 2, cv2.LINE_AA)

            video_output.write(frame)
            cv2.imshow("Goldfish", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        video_output.release()
        cv2.destroyAllWindows()
        # TODO update pedestrian output
        # TODO merge same PID : average height , average gender, average age, time range, start coordinate, end coordinate
        # TODO dump pedestrian output
        output_file = open(self.VIDEO.split('.')[0] + '_data_output.pkl', 'wb')
        pickle.dump(dataset_output_list, output_file)
        output_file.close()
        # print(dataset_output_list)
        goldfishdb.save_data(dataset_output_list)
        goldfishdb.merge_data(dataset_output_list)
        goldfishdb.export_json_original('/Users/michelle/Documents/research/goldfish/original.json')  # TODO：参数是前端对应文件夹路径名
        goldfishdb.export_json_merged('/Users/michelle/Documents/research/goldfish/merged.json')  # TODO：参数是前端对应文件夹路径名

        return

    def set_video(self, input):
        self.VIDEO = input
        return

    # def detect_face(self):
    #     face_cascade = cv2.CascadeClassifier(self.CASE_PATH)
    #
    #     # 0 means the default video capture device in OS
    #     # video_capture = cv2.VideoCapture(0)
    #
    #     video_capture = cv2.VideoCapture('/Users/Sanny02/Desktop/test7.mov')
    #
    #     # infinite loop, break by key ESC
    #     while True:
    #         if not video_capture.isOpened():
    #             sleep(5)
    #         # Capture frame-by-frame
    #         ret, frame = video_capture.read()
    #         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #         faces = face_cascade.detectMultiScale(
    #             gray,
    #             scaleFactor=1.2,
    #             minNeighbors=10,
    #             minSize=(self.face_size, self.face_size)
    #         )
    #         # placeholder for cropped faces
    #         face_imgs = np.empty((len(faces), self.face_size, self.face_size, 3))
    #         for i, face in enumerate(faces):
    #             face_img, cropped = self.crop_face(frame, face, margin=40, size=self.face_size)
    #             (x, y, w, h) = cropped
    #             cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 200, 0), 2)
    #             face_imgs[i,:,:,:] = face_img
    #         if len(face_imgs) > 0:
    #             # predict ages and genders of the detected faces
    #             results = self.model.predict(face_imgs)
    #             predicted_genders = results[0]
    #             ages = np.arange(0, 101).reshape(101, 1)
    #             predicted_ages = results[1].dot(ages).flatten()
    #         # draw results
    #         for i, face in enumerate(faces):
    #             label = "{}, {}".format(int(predicted_ages[i]),
    #                                     "F" if predicted_genders[i][0] > 0.5 else "M")
    #             self.draw_label(frame, (face[0], face[1]), label)
    #
    #         cv2.imshow('Keras Faces', frame)
    #         if cv2.waitKey(5) == 27:  # ESC key press
    #             break
    #     # When everything is done, release the capture
    #     video_capture.release()
    #     cv2.destroyAllWindows()


def get_args():
    parser = argparse.ArgumentParser(description="This script contains pedestrian detection, tracking, face recognition."
                                                 " Also it obtains age, gender and height estimation.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--video", type=str, required=True,
                        help="directory of the video")

    args = parser.parse_args()
    return args


def main():
    args = get_args()
    video_dir = args.video

    face = Goldfish(video_dir=video_dir)

    face.detect_pedestrian()


if __name__ == "__main__":
    main()
