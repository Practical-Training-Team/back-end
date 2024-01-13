import random

import matplotlib
from pydub.exceptions import CouldntDecodeError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import FileResponse, HttpResponse
import io
from builtins import Exception, str, bytes
import sys
import numpy
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread
from pydub import AudioSegment
import xml.etree.ElementTree as ET
from selenium import webdriver
import requests
import numpy as np
import matplotlib.pyplot as plt

#import pyecharts.options as op
#from pyecharts.charts import Radar
from gtts import gTTS, gTTSError
from pydub import AudioSegment
from rest_framework.views import APIView
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from math import pi
from django.http import HttpResponse
from django.http import FileResponse
from gtts import gTTS
from pydub import AudioSegment
import os
from rest_framework.decorators import api_view
import websocket
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import mysql.connector
from server import HOST, USER, PASSWORD, DATABASE
#from rest_framework import viewsets
#from .models import FileModel
#from .serializers import FileSerializer
#from inster import  write_Data
v1 = numpy.empty((1, 5), dtype=int)
sys.path.append("D:\\MyData\\Programs\\python311\\Lib\\site-packages")


host_mysql = HOST
user_mysql = USER
password_mysql = PASSWORD
database_mysql = DATABASE

# 响应用户请求，发送句子相关资源(除音频外)
@api_view(['GET'])
def server_response_sentence(request):
    # 获取参数
    sentence_cate = request.query_params.get('sentence_cate')
    # 定义存储句子
    sentences_return = []
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysql,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        # 返回当前登录用户ID
        cursor = connection.cursor()
        cursor.execute(f'SELECT sentence_id,category,content FROM sentence WHERE category = {sentence_cate}')
        rows = cursor.fetchall()
        # 确保随机数在1到列表长度之间
        num_elements = random.randint(1, min(len(rows),10))
        # 从列表中随机选择num_elements个元素
        random_elements = random.sample(rows, num_elements)
        for row in random_elements:
            if len(row) < 1:
                l = {"sentence_id":None, "category":None, "content":None,"url":None}
                return Response(l)
            sentence_data = {}
            sentence_data["sentence_id"] = row[0]
            sentence_data["category"] = row[1]
            sentence_data["content"] = row[2]
            # 替换为您想检查的文件的路径
            file_path = f"D:/Apache24/www/create_audios/{row[0]}.mp3"
            # 检查文件是否存在
            file_exists = os.path.exists(file_path)
            if not file_exists:
                create_audio_mp3(row[2], row[0])
            sentence_data["url"] = get_create_audio_url(row[0])
            sentences_return.append(sentence_data)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flag = False
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(sentences_return)


def get_text(sentence_id):
    row = ""
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysql,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        # 返回当前登录用户ID
        cursor = connection.cursor()
        cursor.execute(f'SELECT content FROM sentence WHERE sentence_id = {sentence_id}')
        rows = cursor.fetchall()
        row = rows[0][0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flag = False
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        return row


@api_view(['get'])
def analysis_user_audio(request):
    '''
    :param request: user_id, sentence_id and b_audio
    :return: score_dict
    '''
    user_id = request.query_params.get('user_id')
    sentence_id = request.query_params.get('sentence_id')
    b_audio = request.query_params.get('b_audio')
    # dir_path1 = "D:/Apache24/www/users_audios/mp3/3_1.mp3"
    # b_audio = encode_audio_to_base64_string(dir_path1)

    '''
    :function: 音频转换，实现从MP3到m4a格式的转换
    '''
    try:
        input_audio_path_mp3 = b_to_mp3(user_id,sentence_id,b_audio)
        input_audio_file_m4a = change_audio(input_audio_path_mp3,sentence_id)
    except Exception as err:
        print(f"An error occurred when b_to_mp3 and change_audio:{err}")
        return Response({"value": None})
    '''
    : function1: 音频评分
    : function2: 更新grade_record表
    '''
    try:

        content = get_text(sentence_id)

        score_list = audio_evaluation(input_audio_file_m4a,content)
        print("句子分析")
        print(score_list)
        #score_list = [88,97,76,80,75]
    except FileNotFoundError as e:
        print(f"An error occurred when audio_evaluation:{e}")
        return Response({"value": None})
    if len(score_list) > 0:
        insert(user_id,sentence_id,score_list[0])
        # 图片的url地址
    url = picture(user_id, sentence_id,score_list)

    try:
        score_dict = {"url": url, "total_score": score_list[0], "Completeness": score_list[1],
                      "Completeness": score_list[2], "Fluency": score_list[3], "Standard": score_list[4],
                      "Accuracy": score_list[5]}
    except BaseException as e:
        print(f"An error occurred,{e}")
        score_dict = {"url": None, "total_score": None, "Completeness": None,
                      "Completeness": None, "Fluency": None, "Standard": None,
                      "Accuracy": None}
        return (score_dict)

    return Response(score_dict)



# 接受用户录音，返回地址【1】
def b_to_mp3(user_id,sentence_id,b_audio):
    try:
        master_path = "D:/Apache24/www/users_audios/mp3/"
        dir_path = f"{master_path}{user_id}_{sentence_id}.mp3"
        with open(dir_path, "wb") as output_file:
            # 解码二进制字符串
            audio_data = base64.b64decode(b_audio)
            # 将解码后的数据写入文件
            output_file.write(audio_data)
    except TypeError as e:
        print(f"An error occurred when in b_to_mp3,{e}")
        file_path = f"D:/Apache24/www/users_audios/mp3/{user_id}_{sentence_id}.mp3"
        # 检查文件是否存在
        file_exists = os.path.exists(file_path)
        if file_exists:
            os.remove(file_path)

    return dir_path



# 插入成绩记录
def insert(user_id, sentence_id,total_score):
    flag1 = True
    try:

        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysql,
            password=password_mysql,
            database=database_mysql
        )

        if connection.is_connected():
            print("成功连接到MySQL数据库")

        cursor = connection.cursor()
        insert_query = """INSERT INTO grade_record (student_id,sentence_id,grade) VALUES (%s, %s,%s)"""
        data = (user_id, sentence_id, total_score)
        cursor.execute(insert_query, data)
        connection.commit()
    except mysql.connector.Error as err:
        flag1 = False
        print(f"Error: {err}")
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
        if flag1 == False:
            return Response(-1)



#【1】
def audio_evaluation(input_audio_file,content):
    STATUS_FIRST_FRAME = 0
    STATUS_CONTINUE_FRAME = 1
    STATUS_LAST_FRAME = 2

    SUB = "ise"
    ENT = "en_vip"
    CATEGORY = "read_sentence"
    TEXT = '\uFEFF' + content # 文本

    score_list = []

    def convert_to_pcm(input_file, output_file, sample_width=2, channels=1, frame_rate=16000):
        audio = AudioSegment.from_file(input_file)

        if audio.sample_width != sample_width or audio.channels != channels or audio.frame_rate != frame_rate:
            audio = audio.set_sample_width(sample_width)
            audio = audio.set_channels(channels)
            audio = audio.set_frame_rate(frame_rate)

        audio.export(output_file, format="wav")

    class Ws_Param(object):
        def __init__(self, APPID, APIKey, APISecret, AudioFile, Text):
            self.APPID = APPID
            self.APIKey = APIKey
            self.APISecret = APISecret
            self.AudioFile = AudioFile
            self.Text = Text

            self.CommonArgs = {"app_id": self.APPID}
            self.BusinessArgs = {"category": CATEGORY, "sub": SUB, "ent": ENT, "cmd": "ssb",
                                 "auf": "audio/L16;rate=16000",
                                 "aue": "raw", "text": self.Text, "ttp_skip": True, "aus": 1}

        # 生成url
        def create_url(self):
            # wws请求对Python版本有要求，py3.10.4可以正常访问，如果py版本请求wss不通，可以换成ws请求，或者更换py版本
            url = 'ws://ise-api.xfyun.cn/v2/open-ise'
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))

            # 拼接字符串
            signature_origin = "host: " + "ise-api.xfyun.cn" + "\n"
            signature_origin += "date: " + date + "\n"
            signature_origin += "GET " + "/v2/open-ise " + "HTTP/1.1"
            # 进行hmac-sha256进行加密
            signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                     digestmod=hashlib.sha256).digest()
            signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

            authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
                self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
            # 将请求的鉴权参数组合为字典
            v = {
                "authorization": authorization,
                "date": date,
                "host": "ise-api.xfyun.cn"
            }
            # 拼接鉴权参数，生成url
            url = url + '?' + urlencode(v)

            # 此处打印出建立连接时候的url,参考本demo的时候，比对相同参数时生成的url与自己代码生成的url是否一致
            # print("date: ", date)
            # print("v: ", v)
            # print('websocket url :', url)
            return url

    wsParam = Ws_Param(APPID='315a5b43', APISecret='MGIxNzZkNDg2NTAxNmJiMWRkOTRmYWRm',
                       APIKey='e783d658ae382d615656ebf545409d2e',
                       AudioFile='output4.pcm', Text=TEXT)

    def on_message(ws, message):
        nonlocal score_list
        # values = np.zeros(5)
        # feature = ['总分', '完整度分', '流利度分', '标准度分', '准确度分']
        # v1=numpy.empty((1,5), dtype=int)
        # print(f"Sentence Total Score: {'1'}")
        # v1 = np.zeros(5)
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                # print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                data = json.loads(message)["data"]
                status = data["status"]
                result = data["data"]
                if status == 2:
                    xml = base64.b64decode(result)
                    xml_string = xml.decode("gbk")  # 将字节流转换为字符串
                    root = ET.fromstring(xml_string)
                    for sentence in root.findall(".//read_sentence/rec_paper/read_chapter"):
                        v1[0, 0] = (int(float(sentence.attrib["total_score"]) * 20) )
                        v1[0, 1] = (int(float(sentence.attrib["integrity_score"])* 20) )
                        v1[0, 2] = (int(float(sentence.attrib["fluency_score"])* 20) )
                        v1[0, 3] = (int(float(sentence.attrib["standard_score"])* 20) )
                        v1[0, 4] = (int(float(sentence.attrib["accuracy_score"])* 20) )
                    score_list = v1.tolist()[0]
                    # print(f"Sentence Total Score: {v1_list}")
                    print(score_list)

        except Exception as e:
            print("receive msg, but parse exception:", e)

    def on_error(ws, error):
        print("### error:", error)

    def on_close(ws):
        print("### closed ###")

    def on_open(ws):
        def run(*args):
            frameSize = 1280  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

            with open(wsParam.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                    # 第一帧处理
                    # 发送第一帧音频，带business 参数
                    # appid 必须带上，只需第一帧发送
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": wsParam.CommonArgs,
                             "business": wsParam.BusinessArgs,
                             "data": {"status": 0}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"business": {"cmd": "auw", "aus": 2, "aue": "raw"},
                             "data": {"status": 1, "data": str(base64.b64encode(buf).decode())}}
                        ws.send(json.dumps(d))
                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        d = {"business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                             "data": {"status": 2, "data": str(base64.b64encode(buf).decode())}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    # 模拟音频采样间隔
                    time.sleep(intervel)
            ws.close()

        thread.start_new_thread(run, ())

    def run_websocket():
        convert_to_pcm(input_audio_file, 'output4.pcm')
        websocket.enableTrace(False)
        wsParam = Ws_Param(
            APPID='315a5b43',
            APISecret='MGIxNzZkNDg2NTAxNmJiMWRkOTRmYWRm',
            APIKey='e783d658ae382d615656ebf545409d2e',
            AudioFile='output4.pcm',
            Text=TEXT
        )
        wsUrl = wsParam.create_url()
        ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    run_websocket()
    return score_list


@api_view(['GET'])
def picture_view(request):
    l = [[88,97,76,80,75],[90,97,80,80,75],[93,97,80,80,77],[94,97,80,80,80]]
    i = 5
    for k in l:
        picture(4,i,k)
        i = i+1

    return Response(1)

# 绘制可视化，返回url【1】
def picture(user_id,sentence_id,data):
    matplotlib.use('Agg')
    # 数据和标签
    url = ""
    try:
        labels = ["total_score",'Completeness', 'Fluency', 'Standard', 'Accuracy']

        # 计算雷达图的角度
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

        # 使雷达图闭合
        data += data[:1]
        angles += angles[:1]

        # 绘图
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.fill(angles, data, color='red', alpha=0.25)
        ax.plot(angles, data, color='red', linewidth=2)  # 绘制线

        # 设置标签的位置
        ax.set_thetagrids(np.degrees(angles[:-1]), labels)

        # 设置雷达图的范围
        ax.set_ylim(0, 120)

        # 添加标题
        plt.title('Performance Radar Chart')
        master_path = "D:\\Apache24\\www\\images\\"
        dir_path = f"{master_path}" + f"{user_id}_{sentence_id}.png"

        # 保存雷达图到本地文件
        plt.savefig(dir_path, bbox_inches='tight', dpi=300)
        # 关闭图形，避免在 Jupyter Notebook 中显示
        plt.close()
        dir_path_url = "http://10.135.116.43:8080/images/"
        url = dir_path_url + f"{user_id}_{sentence_id}.png"
    except Exception as e:
        print(f"An error occurred when plt:{e}")
    return url


# 获取音频的url【1】
def get_create_audio_url(snetence_id):
    dir_path = "http://10.135.116.43:8080/create_audios/"
    url = dir_path + f"{snetence_id}.mp3"
    return url


# 转换格式，返回地址【1】
def change_audio(input_audio_file_mp3, sentence_id):
    output_audio_file_m4a = ""
    try:
        # 加载音频文件
        audio = AudioSegment.from_file(input_audio_file_mp3)
        print("b")
        # 转换为单声道
        audio = audio.set_channels(1)
        print("c")
        # 设置采样率为 16000Hz
        audio = audio.set_frame_rate(16000)
        # 导出为16位 PCM WAV
        output_audio_file_m4a = ""
        dir_path = "D:/Apache24/www/users_audios/m4a/"
        output_audio_file_m4a = f"{dir_path}" + f"{sentence_id}.m4a"
        print(output_audio_file_m4a)
        audio.export(output_audio_file_m4a, format="mp4")
        print(output_audio_file_m4a)
    except CouldntDecodeError as e:
        print(f"An error occurred while decoding")
    return output_audio_file_m4a


# 创建音频，返回地址【1】
def create_audio_mp3(text, sentence_id):
    try:
        dir_path = "D:/Apache24/www/create_audios"
        output_path = f'{dir_path}/{sentence_id}.mp3'
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
    except gTTSError as e:
        print(f"An error occurred: {e}")

    return output_path


# 将音频文件转换为二进制字符串【1】
def encode_audio_to_base64_string(audio_file_path):
    base64_string = None
    try:
        with open(audio_file_path, "rb") as audio_file:
            # 读取音频文件的二进制数据
            binary_data = audio_file.read()
            # 使用 base64 编码二进制数据
            base64_encoded_data = base64.b64encode(binary_data)
            # 将编码后的数据转换为字符串
            base64_string = base64_encoded_data.decode('utf-8')
    except Exception as e:
        print(f"An error occurred when encode_audio_to_base64_string: {e}")

    return base64_string




# @api_view(['get'])
# def insert_sentence(request):
#     write_Data()
#     return Response(1)


