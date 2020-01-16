import random
import sys
import cv2
from flask import Response, json
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import make_response, jsonify
from flask_cors import CORS
import base64
from person_face_detection.detector import detect_faces
import numpy as np
from PIL import Image
from selfie2simpsons.simpsons_transfer import simpsons_transfer
from PPLM.run_pplm import run_pplm_example
import re
from io import BytesIO
import os
import time

sys.path.append('/home/sannysjtu/google/google-ml-camp/backend/darknet_yolo/')
print(sys.path)
import darknet as dn

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
SIMPSON2ID = {'abraham_grampa_simpson': 0, 'apu_nahasapeemapetilon': 1, 'bart_simpson': 2,
              'charles_montgomery_burns': 3, 'chief_wiggum': 4, 'comic_book_guy': 5, 'edna_krabappel': 6,
              'homer_simpson': 7, 'kent_brockman': 8, 'krusty_the_clown': 9, 'lisa_simpson': 10,
              'marge_simpson': 11, 'milhouse_van_houten': 12, 'moe_szyslak': 13, 'ned_flanders': 14,
              'nelson_muntz': 15, 'principal_skinner': 16, 'raw_character_text': 17, 'sideshow_bob': 18}

STYLE_FILEDIR = '/home/sannysjtu/google/google-ml-camp/style_img_tmp_dir'


def simpson_person_classify(input_path):
    dn.set_gpu(0)
    net = dn.load_net(b"simpsons_test.cfg", b"../../dataset/New_Simpsons/checkpoint/simpsons_5000.weights", 0)
    meta = dn.load_meta(b"simpsons.data")
    files = os.listdir(input_path)

    #res in the r is the detection result of the model
    #the classname is the only required result of our application

    person_class_list = []

    for imgfile in files:
        imgfilepath = os.path.join(input_path, imgfile)
        r = dn.detect(net, meta, imgfilepath.encode('utf-8'))
        current_class_list, current_scores = [], []
        if len(r) < 1:
            best_classname = random.choice(SIMPSON2ID.keys())
        else:
            for res in r:
                classname,score,bbox = res
                classname = classname.decode()
                current_class_list.append(classname)
                current_scores.append(current_scores)
            best_classname = current_class_list[current_scores.index(max(current_scores))]

        person_class_list.append(best_classname)
    return person_class_list


@app.route("/upload", methods=['POST'])
def get_submission():
    IP = request.remote_addr
    # flag[IP] = 0
    # 获取前端传来的json数据
    json_data = request.json
    '''
        {
            name: this.simpson.name, 
            description: this.simpson.description,
            imageBase64: this.simpson.imageBase64,
            others: this.simpson.others,
        }
    '''

    # process data
    text_orig = json_data['description']
    imageBase64 = json_data['imageBase64']
    # base64_data = re.sub('^data:image/.+;base64,', '', imageBase64)
    byte_data = base64.b64decode(imageBase64.split(",")[1])
    image_data = BytesIO(byte_data)
    origin_img = Image.open(image_data)

    # crop face from origin image
    cropped_faces = face_recognition(origin_img)

    # style transfer TODO Note that maybe have more than one face,  need to iter the cropped_faces
    # return the transferred images list
    style_transferred_imgs = simpsons_transfer(cropped_faces)
    this_dir = STYLE_FILEDIR + str(time.time())
    for idx, img in enumerate(style_transferred_imgs):
        cv2.imwrite(os.path.join(this_dir, 'style_img_' + str(idx) + '.jpg'), img)

    # recognize who i am TODO Note that maybe have more than one face,  need to iter the cropped_faces
    # return the classes of images list
    simpson_classes = simpson_person_classify(this_dir)

    # story telling the origin description with personality
    text_results = []
    for simpson_person in simpson_classes:
        text_results.append(
            run_pplm_example(cond_text=text_orig,
                             num_samples=1,
                             discrim='simpson',
                             class_label=SIMPSON2ID[simpson_person],
                             length=25,
                             stepsize=0.01,
                             num_iterations=10,
                             gamma=1.5,
                             kl_scale=0.02,
                             gm_scale=0.95,
                             window_length=5,
                             sample=True,
                             verbosity='quiet')
        )
    results = {}
    for idx, (face, style_transferred_img, simpson_class, simpson_text) in enumerate(zip(cropped_faces,
                                                                                         style_transferred_imgs,
                                                                                         simpson_classes,
                                                                                         text_results)):
        face_base64_str = cv2.imencode('.jpg', face)[1].tostring()
        style_transferred_img_base64_str = cv2.imencode('.jpg', style_transferred_img)[1].tostring()

        results[idx] = {
            'cropped_face': base64.b64encode(face_base64_str).decode('ascii'),
            'simpson_look': base64.b64encode(style_transferred_img_base64_str).decode('ascii'),
            'simpson_person': simpson_class,
            'simpson_talk': simpson_text
        }
    print(results)
    return Response(json.dumps(results), 200, mimetype="application/json")


def crop_face(imgarray, section, margin=40, size=64):
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
    (x1, y1, x2, y2, _) = section
    margin = int(min((x2 - x1), (y2 - y1)) * margin / 100)
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
    cropped = imgarray[y_a: y_b, x_a: x_b]
    resized_img = cv2.resize(cropped, (size, size), interpolation=cv2.INTER_AREA)
    resized_img = np.array(resized_img)
    return resized_img, (x_a, y_a, x_b, y_b)


# face recognition
def face_recognition(img):
    # img = Image.fromarray(img)
    img = img.convert('RGB')
    faces = []
    bounding_boxes, _ = detect_faces(img)
    if len(bounding_boxes) == 1 and (
            bounding_boxes[0][2] > img.size[0] or bounding_boxes[0][3] > img.size[1]):
        raise ValueError
    print("bounding_boxes", bounding_boxes)
    faces.extend(bounding_boxes)

    cropped = []
    for i, face in enumerate(faces):
        print('face', face)
        face_img, cropped = crop_face(img, face, margin=20, size=64)
        cv2.imwrite("./model_data/person_pic/face%s.jpg" % str(i), face_img)
        cropped.append(face_img)
    return cropped


if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
