import random
import sys
import cv2
from flask import Response, json
from flask import Flask
from flask import request, render_template, redirect, url_for
from flask import make_response, jsonify
from flask_cors import CORS
import base64
from google-ml-camp.person_face_detection.detector import detect_faces
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/api/upload", methods = ['POST'])
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
    origin_img = base64.b64decode(imageBase64)

    # crop face from origin image
    cropped_faces = face_recognition(origin_img)

    # style transfer TODO Note that maybe have more than one face,  need to iter the cropped_faces
    # return the transferred images list

    # recognize who i am TODO Note that maybe have more than one face,  need to iter the cropped_faces
    # return the transferred images list

    # story telling the origin description with personality



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
    img = Image.fromarray(img)
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

    # style 

    # class recognition

    # text telling with personality

    # response
    # 查看是否为英文句子，如果不是，则进入交流界面 (mix:小流)
    if json_data['mode'] == 'mix':
        global right_sentence
        global wrong_sentence
        global global_type
        if IP not in right_sentence:
            right_sentence[IP] = ''
        if IP not in wrong_sentence:
            wrong_sentence[IP] = ''
        if len(text_orig) != len(text_orig.encode('utf-8')):
            get_bot_chinese_response = bot_chinese_response.BotChineseResponse('baike_grammar_crawl.pkl', conversation_path='conversation_dict.pkl')
            bot_reply = get_bot_chinese_response(text_orig)
            response = []
            response.append(bot_reply)
            if flag[IP] == 1:
                response = []
                response = ['请修正您的错误，先不要和我闲聊啦~']
                # get_bot_chinese_response = bot_chinese_response.BotChineseResponse('baike_grammar_crawl.pkl', conversation_path='conversation_dict.pkl')
                # response.append(get_bot_chinese_response(text_orig))
            res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 1, 'result': response, 'created': 0}
            return Response(json.dumps(res_dict), 200)

        global global_answers
        # answers = correct_sentence(text_orig)
        # global_answers = answers
        # text = answers[1]

        text = new_query.grammar_check(text_orig)['corrected']
        text_orig = new_query.grammar_check(text_orig)['origin']
        answers = correct_sentence(text_orig, text)

        print('Answers: ')
        print(answers)
        # global_answers[IP] = answers
        correct_type = answers[3]
        if flag[IP] == 0:
            right_sentence[IP] = text

        if right_sentence[IP].replace(' ', '') == text_orig.replace(' ', '') and flag[IP] == 0:
            response = ['你的句子没有语病，请继续努力！']
            res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 1, 'result': response, 'created': 0}

            right_sentence[IP] = ''
            global_type[IP] = []
            return Response(json.dumps(res_dict), 200)

        elif right_sentence[IP] != text_orig and flag[IP] == 0:
            global_answers[IP] = answers
            print('right sentence: ' + right_sentence[IP])
            print('origin sentence: ' + text_orig)
            response = []
            right_sentence[IP] = text
            wrong_sentence[IP] = text_orig
            global_type[IP] = correct_type
            response_sentence = '你的句子可能存在'
            for i in range(len(correct_type)):
                # if correct_type[i] != 'R:ORTH':
                explain = get_type_explain(correct_type[i])
                explain = explain.split('|')[0]
                response_sentence += explain
                response_sentence += ' '
            response_sentence += '等问题，请重新输入句子进行修改。'
            response.append(response_sentence)
            res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 'mix', 'result': response, 'created': 0}
            # 进入纠错的第二层逻辑
            flag[IP] = 1
            return Response(json.dumps(res_dict), 200)

        # flag[IP] == 1即为纠错的第二层逻辑，即用户第一次输入句子错了
        elif right_sentence[IP].replace(' ', '') == text_orig.replace(' ', '') and flag[IP] == 1:
            right_sentence[IP] = ''
            right_sentence[IP] = []
            response = ['恭喜你，这次句子没有问题了，请继续努力哦！']
            res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 'mix', 'result': response, 'created': 0}
            flag[IP] = 0
            return Response(json.dumps(res_dict), 200)

        elif right_sentence[IP] != text_orig and flag[IP] == 1:
            print('right sentence: ' + right_sentence[IP])
            print('origin sentence: ' + text_orig)
            response = []
            response.append('你的句子仍然存在语病，正确句子应该为')
            response.append(right_sentence[IP])
            response_temp = '\n错误的类型有：\n'

            for i in range(len(global_type[IP])):
                print(global_type[IP][i])
                # 将错误句b子经过映射后插入数据库
                insert_sentence(IP_username[IP], IP_password[IP], wrong_sentence[IP], error_map.error_type_map2(global_type[IP][i]))
                if global_type[IP][i].split(':')[0] == 'M' and global_answers[IP][2][i][0] > 0:
                    global_answers[IP][2][i][0] -= 1

                # 读取数据库中存储的explain信息
                explain = get_type_explain(global_type[IP][i])
                explain = explain.replace('|', '. ').replace('*', '{}')
                # answers[2][j]: index
                word1 = [global_answers[IP][0].split()[slice(*arr)] for arr in global_answers[IP][2]]
                print('word1')
                print(word1)
                print('lalala')
                print(global_answers[IP])
                # print(word1[i][0])
                # word2 = [answers[1].split()[slice(*arr)] for arr in answers[2]]
                # 对错误类型的解释，将数据库中对应解释的*替换成相应单词或词组
                print('Explain')
                print(explain)
                explain = explain.format(word1[i][0])
                response_temp += explain
                response_temp += "    "
            right_sentence[IP] = ''
            global_type[IP] = []
            response.append(response_temp)
            # question = get_exercise_according_user(IP_username[IP])[0]
            # response.append(question[1])
            # response.append('\n')
            # response.append('A.'+question[2])
            # response.append('\n')
            # response.append('B.'+question[3])
            # response.append('\n')
            # response.append('C.'+question[4])
            # response.append('\n')
            # response.append('D.'+question[5])
        flag[IP] = 0

        res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 'mix', 'result': response, 'created': 0}
        return Response(json.dumps(res_dict), 200)

    # 小利智能推题
    if json_data['mode'] == 'en':
        IP = request.remote_addr
        global exercise_flag
        if IP not in exercise_flag:
            exercise_flag[IP] = 0
        global one_exercise
        if exercise_flag[IP] == 0:
            response = []
            exercise = ''
            question = get_exercise_according_user(IP_username[IP])[0]
            one_exercise[IP] = question
            exercise += question[1]
            # exercise += '\n'
            # exercise = exercise + 'A.' + question[2] + '    B.' + question[3] + '    C.' + question[4] + '    D.' + question[5]
            response.append(exercise)
            response.append('    A. ' + question[2])
            response.append('    B. ' + question[3])
            response.append('    C. ' + question[4])
            response.append('    D. ' + question[5])
            res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 'en', 'result': response, 'created': 0}
            exercise_flag[IP] = 1
            return Response(json.dumps(res_dict), 200)
        elif exercise_flag[IP] == 1:
            response = []

            if one_exercise[IP][6].strip().lower() == text_orig.strip().lower():
                response.append('恭喜你，答对了！')
            else:
                response.append('很抱歉，正确答案为' + one_exercise[IP][6] + '。请再接再厉')
                if one_exercise[IP][7]:
                    response.append('题目解析：' + one_exercise[IP][7])

                # 将打错的题目加入数据库
                insert_exercise(IP_username[IP], IP_password[IP], one_exercise[IP][1], one_exercise[IP][0])

            one_exercise[IP] = []
            exercise_flag[IP] = 0
            res_dict = {'id': random.randint(0, 999999999), 'text': response, 'user_id': 1, 'mode': 'en', 'result': response, 'created': 0}
            return Response(json.dumps(res_dict), 200)



@app.route("/user", methods = ['GET', 'POST'])
def login():
    # start_qr()
    data = {'typing': '123', 'response': 'test', 'unset': '123456'}
    return Response(json.dumps(data), 200)

@app.route("/user_error", methods = ['POST'])
def return_data():
    IP = request.remote_addr
    global IP_username
    global IP_password
    # 获取前端传来的json数据
    json_data = request.json
    # 发送过来的句子
    user_id = json_data['user_id']
    # 七个技能点：修饰词错误，连接词错误，动词错误，名词形式错误，拼写错误，介词错误，主谓不一致
    wrong_dict = get_exercise_according_user(IP_username[IP])[1]
    sum_wrong = wrong_dict['R:ADJ'] + wrong_dict['R:CONJ']
    + wrong_dict['R:VERB'] + wrong_dict['R:NOUN'] + wrong_dict['R:OTHER']
    + wrong_dict['R:PREP'] + wrong_dict['SVA']
    sum_wrong -= 1
    R_ADJ = wrong_dict['R:ADJ']
    R_CONJ = wrong_dict['R:CONJ']
    R_VERB = wrong_dict['R:VERB']
    R_NOUN = wrong_dict['R:NOUN']
    R_OTHER = wrong_dict['R:OTHER']
    R_PREP = wrong_dict['R:PREP']
    SVA = wrong_dict['SVA']
    data = {
        'err_types': [
            { 'type': '修饰词错误', 'freq': R_ADJ-1 },
            { 'type': '连接词错误', 'freq': R_CONJ-1 },
            { 'type': '动词错误', 'freq': R_VERB-1 },
            { 'type': '名词形式错误', 'freq': R_NOUN-1 },
            { 'type': '拼写错误', 'freq': R_OTHER-2 },
            { 'type': '介词错误', 'freq': R_PREP-1},
            { 'type': '主谓不一致', 'freq': SVA-1 }
            ]
        }

    # print(json.dumps(data))
    return Response(json.dumps(data), 200)

@app.route("/report", methods = ['POST'])
def report():
    IP = request.remote_addr
    global IP_username
    global IP_password
    # 七个技能点：修饰词错误，连接词错误，动词错误，名词形式错误，拼写错误，介词错误，主谓不一致
    wrong_dict = get_exercise_according_user(IP_username[IP])[1]
    sum_wrong = wrong_dict['R:ADJ'] + wrong_dict['R:CONJ'] + wrong_dict['R:VERB'] + wrong_dict['R:NOUN'] + wrong_dict['R:OTHER'] + wrong_dict['R:PREP'] + wrong_dict['SVA']
    sum_wrong -= 1
    R_ADJ = wrong_dict['R:ADJ']
    R_CONJ = wrong_dict['R:CONJ']
    R_VERB = wrong_dict['R:VERB']
    R_NOUN = wrong_dict['R:NOUN']
    R_OTHER = wrong_dict['R:OTHER']
    R_PREP = wrong_dict['R:PREP']
    SVA = wrong_dict['SVA']

    # 第一次映射的种类
    T = get_exercise_according_user2(IP_username[IP])[1]
    # print(T)
    # 平滑
    P = 1
    report = {
        'data': {
                "numbers": [round((T['R:ADJ']+P)/(sum_wrong+P)*100, 2), round((T['R:ADV']+P)/(sum_wrong+P)*100, 2), round((T['R:CONJ']+P)/(sum_wrong+P)*100, 2), round((T['R:DET']+P)/(sum_wrong+P)*100, 2),
                round((T['R:NOUN']+P)/(sum_wrong+P)*100, 2), round((T['R:NOUN:NUM']+P)/(sum_wrong+P)*100, 2), round((T['R:PREP']+P)/(sum_wrong+P)*100, 2), round((T['R:PRON']+P)/(sum_wrong+P)*100, 2),
                round((T['R:PUNCT']+P)/(sum_wrong+P)*100, 2), round((T['R:VERB']+P)/(sum_wrong+P)*100, 2), round((T['R:CONTR']+P)/(sum_wrong+P)*100, 2), round((T['R:MORPH']+P)/(sum_wrong+P)*100, 2),
                round((T['R:ORTH']+P)/(sum_wrong+P)*100, 2), round((T['R:OTHER']+P)/(sum_wrong+P)*100, 2), round((T['R:SPELL']+P)/(sum_wrong+P)*100, 2), round((T['R:WO']+P)/(sum_wrong+P)*100, 2), round((T['R:VERB:FORM']+P)/(sum_wrong+P)*100, 2),
                round((T['R:VERB:TENSE']+P)/(sum_wrong+P)*100, 2), round((T['R:VERB:INFL']+P)/(sum_wrong+P)*100, 2), round((T['R:VERB:SVA']+P)/(sum_wrong+P)*100, 2),
                ],
                "wrongTypes": ["形容词错误", "副词错误", "连接词错误", "限定词错误", "名词使用错误", "名词单复数",
                                "介词错误","代词错误", "标点符号错误", "动词错误", "缩略形式错误",
                                "相同词源但是词性错误", "大小写或空格错误", "其他错误", "拼写错误",
                                "词的顺序错误", "动词形式", "动词时态错误", "动词词性变换",
                                "主谓不一致"],
                "skill":[round((R_ADJ/sum_wrong)*150, 2), round((R_CONJ/sum_wrong)*150, 2), round((R_VERB/sum_wrong)*150, 2), round((R_NOUN/sum_wrong)*150, 2), round(((R_OTHER-1)/sum_wrong)*150, 2), round((R_PREP/sum_wrong)*150, 2), round((SVA/sum_wrong)*150, 2)]
            }
    }
    print(report)
    return Response(json.dumps(report), 200)

@app.route("/recommend", methods = ['POST'])
def recommend():
    global IP_username
    global IP_password
    IP = request.remote_addr
    global exercise_flag
    # exercise_flag[IP] = 0
    global one_exercise
    if IP not in exercise_flag:
        exercise_flag[IP] = 1
    json_data = request.json
    wrong_type = json_data['type']
    wrong_dict = {
    '修饰词错误': 'R:ADJ',
    '连接词错误': 'R:CONJ',
    '动词错误': 'R:VERB',
    '名词形式错误': 'R:NOUN',
    '拼写错误': 'R:OTHER',
    '介词错误': 'R:PREP',
    '主谓不一致': 'SVA',
    }
    wrong_type = wrong_dict[wrong_type]
    exercise = get_rand_execise_from_list(get_mapped_type(wrong_type))
    one_exercise[IP] = exercise
    response = []
    response_temp = exercise[1]
    response_temp += '\n'
    response_temp = response_temp + 'A.' + exercise[2] + '    B.' + exercise[3] + '    C.' + exercise[4] + '    D.' + exercise[5]
    response.append(response_temp)
    exercise_flag[IP] = 1
    res_dict = {'id': random.randint(0, 999999999), 'result': response, 'user_id': 1, 'mode': 'en', 'result': response, 'created': 0}
    return Response(json.dumps(res_dict), 200)

@app.route("/user_register", methods = ['POST'])
def register():
    IP = request.remote_addr
    global IP_username
    global IP_password

    json_data = request.json
    print(json_data)
    username = json_data['user']
    password = json_data['password']
    repassword = json_data['repassword']

    if username == '' or password == '' or repassword == '':
        res_dict = {'id': random.randint(0, 999999999), 'number': 4}
        # 注册时字段不能为空
        return Response(json.dumps(res_dict), 200)

    if password != repassword:
        res_dict =  {'id': random.randint(0, 999999999), 'number': 2}
        # 密码和确认密码不一致
        return Response(json.dumps(res_dict), 200)

    sql = """SELECT * FROM WECHAT_USER_SENTENCE WHERE UID = ('%s')"""
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(sql % (username))
        answers = cursor.fetchall()
        conn.close()
    except:
        print("Getting WECHAT_USER_SENTENCE1 failed!")
        conn.close()

    if not answers:
        sql = """INSERT INTO WECHAT_USER_SENTENCE (UID, NICKNAME, WRONG_SENTENCE, WRONG_TYPE)
                VALUES ('%s', '%s', '%s', '%s')"""
        conn = connect_database()
        try:
            cursor = conn.cursor()
            cursor.execute(sql % (username, password, ' ', 'UNK'))
            conn.commit()
            conn.close()
            IP_username[IP] = username
            IP_password[IP] = password
            res_dict =  {'id': random.randint(0, 999999999), 'number': 3}
            # 注册成功
            return Response(json.dumps(res_dict), 200)
        except:
            print("Insert WECHAT_USER_SENTENCE1 failed!")
            conn.close()
            res_dict =  {'id': random.randint(0, 999999999), 'number': 1}
            # 注册失败
            return Response(json.dumps(res_dict), 200)
    else:
        res_dict =  {'id': random.randint(0, 999999999), 'number': 1}
        return Response(json.dumps(res_dict), 200)

@app.route("/user_login", methods = ['POST'])
def loginin():
    IP = request.remote_addr
    global IP_username
    global IP_password

    json_data = request.json
    print(json_data)
    username = json_data['user']
    password = json_data['password']

    sql = """SELECT * FROM WECHAT_USER_SENTENCE WHERE UID = ('%s') AND NICKNAME = ('%s')"""
    try:
        conn = connect_database()
        cursor = conn.cursor()
        cursor.execute(sql % (username, password))
        answers = cursor.fetchall()
        conn.close()
    except:
        print("Getting WECHAT_USER_SENTENCE2 failed!")
        conn.close()
        res_dict =  {'id': random.randint(0, 999999999), 'number': 0}
        # 发生错误
        return Response(json.dumps(res_dict), 200)
    if answers:
        IP_username[IP] = username
        IP_password[IP] = password
        res_dict =  {'id': random.randint(0, 999999999), 'number': 1}
        # 登陆成功
        return Response(json.dumps(res_dict), 200)
    else:
        res_dict =  {'id': random.randint(0, 999999999), 'number': 0}
        # 登陆失败
        return Response(json.dumps(res_dict), 200)


if __name__ == '__main__':
    new_query.init_fn()
    app.run(debug = True, port = 8000, host = "")
