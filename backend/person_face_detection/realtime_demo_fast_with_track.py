# -*- coding: UTF-8 -*-
import cv2
import os
from time import sleep
import numpy as np
import argparse
from wide_resnet import WideResNet
from keras.utils.data_utils import get_file
import time
from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from deep_sort.detection import Detection as ddet
import pickle as pkl

class Goldfish(object):
    """
    Singleton class for face recongnition task
    """
    CASE_PATH = "./pretrained_models/haarcascade_frontalface_alt.xml"
    WRN_WEIGHTS_PATH = "./pretrained_models/weights.18-4.06.hdf5"
    PROTO = "./pretrained_models/deploy.prototxt"
    MOBILE_CAFFE = "./pretrained_models/mobilenet_iter_73000.caffemodel"
    COLORS = (0, 255, 0)
    CONFIDENCE_THRESHOLD = 0.2
    PEDESTRIAN_YOLO = './model_data/mars-small128.pb'
    VIDEO = '/Users/Sanny02/Desktop/test_lighted.mp4'
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

    def __new__(cls, weight_file=None, depth=16, width=8, face_size=64):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Goldfish, cls).__new__(cls)
        return cls.instance

    def __init__(self, depth=16, width=8, face_size=64):
        self.face_size = face_size
        self.ag_model = WideResNet(face_size, depth=depth, k=width)()
        model_dir = os.path.join(os.getcwd(), "pretrained_models").replace("//", "\\")
        fpath = get_file('weights.18-4.06.hdf5',
                         self.WRN_WEIGHTS_PATH,
                         cache_subdir=model_dir)
        self.ag_model.load_weights(fpath)
        self.pedestrian_model = cv2.dnn.readNetFromCaffe(self.PROTO, self.MOBILE_CAFFE)
        self.face_cascade = cv2.CascadeClassifier(self.CASE_PATH)
        self.pedestrian_model_input_encoder = gdet.create_box_encoder(self.PEDESTRIAN_YOLO, batch_size=1)
        self.metric = nn_matching.NearestNeighborDistanceMetric('cosine', self.MAX_COSINE_DISTANCE, self.NN_BUDGET)
        self.pedestrian_tracker = Tracker(self.metric)

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
        if section is None:
            section = [0, 0, img_w, img_h]
        (x, y, w, h) = section
        margin = int(min(w ,h) * margin / 100)
        x_a = x - margin
        y_a = y - margin
        x_b = x + w + margin
        y_b = y + h + margin
        if x_a < 0:
            x_b = min(x_b - x_a, img_w-1)
            x_a = 0
        if y_a < 0:
            y_b = min(y_b - y_a, img_h-1)
            y_a = 0
        if x_b > img_w:
            x_a = max(x_a - (x_b - img_w), 0)
            x_b = img_w
        if y_b > img_h:
            y_a = max(y_a - (y_b - img_h), 0)
            y_b = img_h
        cropped = imgarray[y_a: y_b, x_a: x_b]
        resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
        resized_img = np.array(resized_img)
        return resized_img, (x_a, y_a, x_b - x_a, y_b - y_a)

    def crop_person(self, imgarray, section, margin=40, size=64):
        """
        :param imgarray: full image
        :param section: person detected area (x1, y1, x2, y2)

        """
        img_h, img_w, _ = imgarray.shape
        if section is None:
            section = [0, 0, img_w, img_h]
        # (x1, y1, x2, y2) = section
        # margin = int(min(w, h) * margin / 100)
        (x_l, y_l, x_r, y_h) = (section * np.array([img_w, img_h, img_w, img_h])).astype('int')


        cropped = imgarray[y_l: y_h, x_l: x_r]
        # resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
        # resized_img = np.array(resized_img)
        return cropped

    def to_xlwh(self, sections):
        # return x, y, w, h
        ret = sections.copy()
        ret[:, 2:] -= ret[:, :2]
        return ret

    def detect_pedestrian(self):
        video_capture = cv2.VideoCapture(self.VIDEO)
        fourcc = cv2.VideoWriter_fourcc(*'MP42')
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        # fps = video_capture.get(5)
        size = (int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        video_output = cv2.VideoWriter(self.VIDEO.split('.')[0] + '_out.mp4',
                                       fourcc,
                                       fps, size)
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
        while True:
            if not video_capture.isOpened():
                sleep(5)
            tic = time.time()
            ret, frame = video_capture.read()
            frame_index += 1
            # todo get frame of per second ??? get more quicker computation of one video
            # if frame_index % fps is not 0:
            #     continue

            # time of this frame in the video
            current_time = video_capture.get(0)

            (height, width) = frame.shape[:2]
            # blob images by resizing images to a fixed 300*300 pixels and bath normalized
            blob_images = cv2.dnn.blobFromImage(cv2.resize(frame, (300,300)), 0.007843, size=(300,300), mean=127.5)

            print("Computing Pedestrian Detection...")
            self.pedestrian_model.setInput(blob_images)
            objects = self.pedestrian_model.forward()
            objects = objects[0, 0, :]

            pedestrians = np.asarray([obs for obs in objects if int(obs[1]) == self.CLASSES.index('person')
                                      and obs[2] > self.CONFIDENCE_THRESHOLD])

            if len(pedestrians) > 0:
                print(pedestrians)
                pedestrians_to_track = pedestrians[:, 3:]

                boxes = self.to_xlwh(pedestrians_to_track * np.array([width, height, width, height]))

                # extract img of persons in the whole frame
                features = self.pedestrian_model_input_encoder(frame, boxes)

                detections = [Detection(box, detected_pedestrian[2], feature) for box, feature, detected_pedestrian in zip(boxes, features, pedestrians)]

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
                for track in self.pedestrian_tracker.tracks:
                    if not track.is_confirmed() or track.time_since_update > 1:
                        continue
                    # return min_x, min_y, max_x, max_y
                    bbox = track.to_tlbr()
                    # PID of each person in the video
                    person_id = track.track_id
                    # todo get occurrence time of this person in this video
                    # track.age : int total number of frames since first occurance.
                    # if track.track_id => has_value?
                    cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255), 2)
                    cv2.putText(frame, str(track.track_id), (int(bbox[0]), int(bbox[1])), 0, 5e-3 * 200, (0, 255, 0), 2)

            print("Finding Face...")
            faces = []
            whole_bodys = []
            full_detected_persons = []
            # todo if no faces detected in one pedestrian
            if len(pedestrians) > 0:
                for pedestrian_dectection in pedestrians:
                    whole_body = self.crop_person(frame, pedestrian_dectection[3:])
                    gray = cv2.cvtColor(whole_body, cv2.COLOR_BGR2GRAY)
                    face = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.2,
                        minNeighbors=10,
                        minSize=(self.face_size, self.face_size)
                    )
                    if len(face) == 1:
                        whole_bodys.append(whole_body)
                        faces.extend(face)
                        full_detected_persons.append(pedestrian_dectection[3:] * np.array([width, height, width, height]))

            # placeholder for cropped faces
            face_imgs = np.empty((len(faces), self.face_size, self.face_size, 3))
            for i, face in enumerate(faces):
                print(face)
                face_img, cropped = self.crop_face(whole_bodys[i], face, margin=40, size=self.face_size)
                (x, y, w, h) = cropped
                cv2.rectangle(frame, (int(x + full_detected_persons[i][0]), int(y + full_detected_persons[i][1])),
                              (int(x + full_detected_persons[i][0] + w), int(y + full_detected_persons[i][1] + h)),
                              (255, 200, 0), 2)
                face_imgs[i, :, :, :] = face_img
            if len(face_imgs) > 0:
                # predict ages and genders of the detected faces
                results = self.ag_model.predict(face_imgs)
                predicted_genders = results[0]
                ages = np.arange(0, 101).reshape(101, 1)
                predicted_ages = results[1].dot(ages).flatten()
            # draw results
            for i, face in enumerate(faces):
                label = "{}, {}".format(int(predicted_ages[i]),
                                        "Female" if predicted_genders[i][0] > 0.5 else "Male")
                self.draw_label(frame,
                                (face[0] + int(full_detected_persons[i][0]), face[1] + int(full_detected_persons[i][1])),
                                label)

            # pedstrian time, coordinate, height
            if pedestrians.size > 0:
                # get x, y coordinate of every person in this frame
                person_coordinate = pedestrians[:, [3, 4, 5, 6]] * np.array([width, height, width, height])
                person_coordinate = person_coordinate.astype('int')

                # cot(x)
                aspect_ratio = 1.0 * (person_coordinate[:, 2] - person_coordinate[:, 0])\
                               / (person_coordinate[:, 3] - person_coordinate[:, 1])
                new_aspect_ratio = aspect_ratio.reshape((aspect_ratio.size, 1))

                # define aspect ratio range
                aspect_ratio_range_lower = 0.35
                aspect_ratio_range_upper = 0.45

                # N * 5
                new_person_coordinate = np.append(person_coordinate, new_aspect_ratio, axis=1)
                final_person_coordinate_list = []
                # if aspect ratio in range(0.35,0.45), processing and ddraw reference plane
                for idx, val in enumerate(new_person_coordinate):
                    final_person_coordinate_list.append(new_person_coordinate[idx])
                    final_person_coordinate_array = np.array(final_person_coordinate_list)

                    final_height_range = final_person_coordinate_array[:, [1, 3]]
                    final_width_range = final_person_coordinate_array[:, [0, 2]]

                    final_height_len = final_height_range[:, 1] - final_height_range[:, 0]
                    final_width_len = final_width_range[:, 1] - final_height_range[:, 0]

                    height_median = np.median(final_height_len)
                    height_mean = np.mean(final_height_len)

                    median_index = np.nanargmin(np.abs(final_height_len - height_median))
                    mean_index = np.nanargmin(np.abs(final_height_len - height_mean))

                    median_index_y1 = final_height_range[median_index][0]
                    median_index_y2 = final_height_range[median_index][1]

                    mean_index_y1 = final_height_range[mean_index][0]
                    mean_index_y2 = final_height_range[mean_index][1]

                reference_plane_scale = 0.2

                # background box
                # cv2.rectangle(frame, (0, int(median_index_y1 * (1 - reference_plane_scale))),
                #               (width, int(median_index_y2 * (1 + reference_plane_scale))), (211, 211, 211), 2)

                height_scale = 0.2

                for person in pedestrians:
                    confidence = person[2]

                    # bounding box real coordinate
                    box = person[3: ] * np.array([width, height, width, height])
                    (x1, y1, x2, y2) = box.astype('int')
                    # probabiltiy of person
                    # label = "人: %.2f%%"%(confidence * 1.0)
                    label = "Person: %.2f%%"%(confidence * 1.0)

                    # draw a box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), self.COLORS, 2)

                    # add label text on the box
                    y = y1 - 15 if y1 - 15 > 15 else y1 + 15
                    cv2.putText(frame, label, (x1, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLORS, 2)

                    if y2 - y1 <  int(median_index_y1 * (1 + 2 * reference_plane_scale)):
                        if y2 - y1 > height_median * (1 + height_scale):
                            height_label = "Body Type: Heigh"
                            cv2.putText(frame, height_label, (x1, y1 - 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (211, 211, 211), 2)
                        if height_median * (1 + height_scale) > y2 - y1 > height_median * (1 - height_scale):
                            height_label = "Body Type: Median"
                            cv2.putText(frame, height_label, (x1, y1 - 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (211, 211, 211), 2)
                        if y2 - y1 > height_median * (1 + height_scale):
                            height_label = "Body Type: Short"
                            cv2.putText(frame, height_label, (x1, y1 - 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (211, 211, 211), 2)

            toc = time.time()
            durr = float(toc - tic)
            print_fps = 1.0 / durr
            cv2.putText(frame, "fps: %.3f"%print_fps, (20, 20), 2, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, "Current Time: %.3f sec" % (current_time / 1000), (int(width * 0.65), 20), 2, 0.8, (0, 0, 255), 2, cv2.LINE_AA)

            video_output.write(frame)
            cv2.imshow("Goldfish", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        video_output.release()
        cv2.destroyAllWindows()
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
    parser = argparse.ArgumentParser(description="This script detects faces from web cam input, "
                                                 "and estimates age and gender for the detected faces.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--depth", type=int, default=16,
                        help="depth of network")
    parser.add_argument("--width", type=int, default=8,
                        help="width of network")
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    depth = args.depth
    width = args.width

    face = Goldfish(depth=depth, width=width)

    face.detect_pedestrian()


if __name__ == "__main__":
    main()
