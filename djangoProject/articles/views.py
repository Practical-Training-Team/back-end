import csv
import os
import matplotlib
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
from gtts import gTTS
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

v1 = numpy.empty((1, 5), dtype=int)
sys.path.append("D:\\MyData\\Programs\\python311\\Lib\\site-packages")
from django.shortcuts import render
from gtts import gTTS
from pydub import AudioSegment
from pyparsing import results
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
import mysql.connector
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from server import HOST, USER, PASSWORD, DATABASE
import random
#from  inster  import write_Data
import requests
from PIL import Image
from io import BytesIO
import matplotlib
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
# Create your views here.


name = ["id", "content"]
host_mysql = HOST
user_mysql = USER
password_mysql = PASSWORD
database_mysql = DATABASE
account_list = []
password_list = []
article_content = []
articles_return = []

# 用户传来用户id，函数解析，查找相应的内容，返回
@api_view(['GET'])
def get_articles(request):
    user_id = request.query_params.get('user_id')
    article_id, article_features = get_article_features()
    user_feature = get_user_features(user_id)
    similarity_score = []
    article_id_list = []
    result_list = []
    for id in article_id:
        article_id_list.append(id[0])
    if user_feature:
        # 将用户特征向量和文章特征向量转化为NumPy数组
        np_user_vector = np.array(user_feature)
        np_article_vector = np.array(article_features)

        new_array = np.zeros((np_article_vector.shape[0], 6))
        new_array[:, :np_article_vector.shape[1]] = np_article_vector
        # 计算余弦相似度
        for i in range(7):
            similarity_score.append(cosine_similarity([np_user_vector], [new_array[i]])[0][0])
        id_future_s = dict(zip(article_id_list,similarity_score))
        id_future_s_sorted = sorted(id_future_s.items(),key=lambda x:x[1],reverse=True)
        for element in id_future_s_sorted:
            result_list.append(element[0])
    else:
        num_articles = min(5, len(article_id_list))
        result_list = random.sample(article_id_list, num_articles)
    articles_return = get_article_content(result_list)
    articles_return_list = []
    titles = ["article_id","title","category","content","likes","page_view","release_time","image"]
    flag = True
    for article in articles_return:
        ll = dict(zip(titles,article[0]))
        articles_return_list.append(ll)
    return Response(articles_return_list)


@api_view(['GET'])
def increase_article_thumb(request):
    user_id = request.query_params.get('user_id')
    article_id = request.query_params.get('article_id')
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysql,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")

        # 参数化的 SQL 查询
        query = "SELECT like_or_not FROM likes WHERE user_id = %s AND article_id = %s"
        cursor = connection.cursor()
        cursor.execute(query, (user_id, article_id))
        flag = cursor.fetchall()
        if len(flag) < 1 :
            insert_query = "INSERT INTO likes (user_id, article_id, like_or_not) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (user_id, article_id, 1))
            connection.commit()

            update_query = "UPDATE articles SET likes = likes + 1,page_view = page_view + 1 WHERE  article_id = %s"
            cursor.execute(update_query, [article_id])
            connection.commit()
        else:
            return Response(-1)
        # else:
        #     update_query = "UPDATE likes SET like_or_not = 1 WHERE  article_id = %s and user_id = %s"
        #     cursor.execute(update_query, (user_id, article_id))
        #     connection.commit()
        #     update_query = "UPDATE likes SET like_or_not = 1 WHERE  article_id = %s and user_id = %s"

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return Response(-1)

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return Response(1)

# 获取单个文章内容
@api_view(['GET'])
def get_single_article_content(request):
    article_id = request.query_params.get('article_id')
    category_id = request.query_params.get('category_id')
    user_id = request.query_params.get('user_id')
    #article_id = 5
    """
    结果以列表形式返回，列表元素为若干字典，具体如下：
    1. 第一个元素：【"article_id","title","category","likes","page_view","release_time","image"】
    2. 其余的字典包括【段落id，文章分段内容，文章读音，文章分析结果，文章内容】
    """
    print(article_id,category_id,user_id)
    categroys = {0:"life", 3:"work", 2:"recreation",1:"travel", 5: "sport", 4:"technology"}
    print(categroys)
    try:
        increase_page_views(article_id)
        print("increae_page_views")
        increae_user_read_num(user_id,category_id)
        print("increae_user_read_num")
    except  Exception as e:
        print(f"update,{e}")
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
        sql = "SELECT article_id,title,category,content,likes,page_view,release_time,image  FROM articles WHERE article_id = %s"
        cursor.execute(sql,[article_id])
        print("sql")
        rows = cursor.fetchall()
        print(rows)
        # 第一个字典中的信息
        dict1 = {}
        text = ""

        try:
            dict1["article_id"] =rows[0][0]
            dict1["title"] = rows[0][1]
            dict1["category"] = rows[0][2]
            dict1["likes"] = rows[0][4]
            dict1["page_view"] = rows[0][5]
            dict1["release_time"] = rows[0][6]
            dict1["image"] = rows[0][7]

            # 第二个字典中的信息
            text = rows[0][3]
        except Exception as e:
            print(f"An error occurs when select sql,{e}")
            return_dict = {"article_id":None ,"title":None ,"category":None,"likes":None,"page_view":None,"release_time":None,"image":None,"content":None}
            return Response(return_dict)

        # 存储信息
        # result.append(dict1)

        # 按换行符分割文本
        paragraphs = text.strip().split('\n')
        # 输出列表，其中每个元素是一个段落
        for_dict2_list = []
        for i, paragraph in enumerate(paragraphs, 1):
            dict2 = {}
            dict2["paragraph_id"] = i
            dict2["text"] = paragraph
            audio_url = create_article_audio_mp3(paragraph,article_id,i)
            print(audio_url)
            dict2["audio"] = audio_url
            for_dict2_list.append(dict2)
        dict1["content"] = for_dict2_list
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(dict1)
    #return Response(1)



# 用以创建文章音频

def create_article_audio_mp3(text,article_id,paragraph_id):
    # 替换为您想检查的文件的路径
    output_path = f"D:/Apache24/www/article_audios/{article_id}_{paragraph_id}.mp3"
    # 检查文件是否存在
    file_exists = os.path.exists(output_path)
    if not file_exists:
        tts = gTTS(text=text, lang='en')
        tts.save(output_path)
    dir_path_url = "http://10.135.116.43:8080/article_audios/"
    url = dir_path_url +  f"{article_id}_{paragraph_id}.mp3"
    return url


'''
            # 替换为您想检查的文件的路径
            file_path = f"D:/Apache24/www/create_audios/{row[0]}.mp3"
            # 检查文件是否存在
            file_exists = os.path.exists(file_path)
            if not file_exists:
                create_audio_mp3(row[2], row[0])
'''


@api_view(['GET'])
def article_popularity_list(request):
    # 计算文章的浏览量和点赞量（加权），数据库返回文章ID和文章浏览量以及点赞量
    article_id_list = []
    article_popularity_list = []
    articles_return = []
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
        cursor.execute(f'SELECT article_id,likes,page_view FROM articles')
        rows1 = cursor.fetchall()
        print(rows1[0])
        print(type(rows1))
        article_popularity_dict = {}
        for row in rows1:
            article_popularity_dict[row[0]] = row[1] * 0.6 + row[2] * 0.4
        print("article_popularity_dict")
        print(type(rows1))
        print(rows1[0])
        print(article_popularity_dict[rows1[0][0]])
        article_popularity_dict_sorted = sorted(article_popularity_dict.items(), key=lambda x: x[1], reverse=True)
        k = 0
        flag3 = True

        for element in article_popularity_dict_sorted:
            if flag3 == True:
                print(element)
                article_popularity_list.append(element[0])
            k  = k + 1
            if k == 5:
                flag3 = False

        articles_return = get_article_content(article_popularity_list)
        articles_return_list = []
        titles = ["article_id", "title", "category", "content", "likes", "page_view", "release_time", "image"]
        flag = True
        for article in articles_return:
            if flag == True:
                print(article)
                flag = False
            ll = dict(zip(titles, article[0]))
            articles_return_list.append(ll)
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return Response(articles_return_list)

# 获取图片大小
@api_view(['GET'])
def pictures_classify(request):
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
        cursor.execute(f'SELECT article_id,image FROM articles')
        rows1 = cursor.fetchall()
        print(rows1[0])
        print(type(rows1))
        picture_url_list = []
        flag = True
        for row in rows1:
            if flag == True:
                print(row)
                flag = False
            picture_url_list.append(row)

        flag1 = True
        classify_picture_dict = {}

        i = 0

        picture_size_list = []

        for picture_url in picture_url_list:
            i = i + 1
            response = requests.get(picture_url[1])
            image = Image.open(BytesIO(response.content))

            if flag1 == True:
                print(image.size)
                print(picture_url)
                flag1 = False
            if image.size in picture_size_list: # 键值可获取
                key = picture_size_list.index(image.size) # 获取键值
                #print(0)
                if key in classify_picture_dict: # 键值在字典中
                    if classify_picture_dict[key] == []: # 访问该键值，判断其值是否为空列表
                        classify_picture_dict[key] =[]
                        classify_picture_dict[key].append(picture_url[0])
                        #print(1)
                    else:#键值不为空列表
                        classify_picture_dict[key].append(picture_url[0])
                        #print(2)
                else:
                    classify_picture_dict[key] = []
                    classify_picture_dict[key].append(picture_url[0])
                    #print(3)
            else:# 键值不可获取
                picture_size_list.append(image.size)
                key = picture_size_list.index(image.size)
                #print(4)
                if key in classify_picture_dict:
                    if classify_picture_dict[key] == []:
                        classify_picture_dict[key] = []
                        classify_picture_dict[key].append(picture_url[0])
                        #print(5)
                    else:
                        classify_picture_dict[key].append(picture_url[0])
                        #print(6)
                else:
                    classify_picture_dict[key] = []
                    classify_picture_dict[key].append(picture_url[0])
                    #print(classify_picture_dict[key])
                    #print(7)

            if i >= 50:
                return Response(classify_picture_dict)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(classify_picture_dict)


# 搜索文章

@api_view(['GET'])
def search(request):
    keywords = request.query_params.get('keywords')
    search_result_list = search_by_keyword(keywords)

    articles_return = get_article_content(search_result_list)
    articles_return_list = []
    titles = ["article_id","title","category","content","likes","page_view","release_time","image"]
    flag = True
    for article in articles_return:
        if flag == True:
            print(article)
            flag = False
        ll = dict(zip(titles,article[0]))
        articles_return_list.append(ll)

    #print(articles_return)

    return Response(articles_return_list)





@api_view(['get'])
def analysis_user_audio(request):
    '''
    :param request: user_id, sentence_id and b_audio
    :return: score_dict
    '''
    user_id = request.query_params.get('user_id')
    article_id = request.query_params.get('article_id')
    paragraph_id = request.query_params.get('paragraph_id')
    b_audio = request.query_params.get('b_audio')
    # dir_path1 = f"D:\\Apache24\\www\\users_audios\\mp3\\3_1.mp3"
    # b_audio = encode_audio_to_base64_string(dir_path1)
    score_dict = {}

    '''
    :function: 音频转换，实现从MP3到m4a格式的转换
    '''
    input_audio_path_mp3 = b_to_mp3(user_id,article_id,paragraph_id,b_audio)
    input_audio_file_m4a = change_audio(input_audio_path_mp3,article_id,paragraph_id)
    '''
    : function1: 音频评分
    : function2: 更新grade_record表
    '''
    content = get_text(paragraph_id)
    score_list = audio_evaluation(input_audio_file_m4a,content)
    #score_list = [90,85,78,98,65]
    print(score_list)
    if len(score_list) > 0:
        insert(user_id,article_id,paragraph_id,score_list[0])
        # 图片的url地址
    url = picture(user_id, article_id,paragraph_id,score_list)
    score_dict = {"url": url, "total_score": score_list[0], "Completeness": score_list[1], "Completeness": score_list[2],"Fluency": score_list[3],"Standard": score_list[4],"Accuracy": score_list[5]}
    return Response(score_dict)


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




# 接受用户录音，返回地址【1】
def b_to_mp3(user_id,article_id,paragraph_id,b_audio):
    master_path = f"D:/Apache24/www/users_audios/mp3/"
    dir_path = f"{master_path}{user_id}_{article_id}_{paragraph_id}.mp3"
    with open(dir_path, "wb") as output_file:
        # 解码二进制字符串
        audio_data = base64.b64decode(b_audio)
        # 将解码后的数据写入文件
        output_file.write(audio_data)
    return dir_path

# 插入成绩记录
def insert(user_id, article_id,paragraph_id,total_score):
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
        data = (user_id, article_id,paragraph_id, total_score)
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


def audio_evaluation(input_audio_file,text):
    STATUS_FIRST_FRAME = 0
    STATUS_CONTINUE_FRAME = 1
    STATUS_LAST_FRAME = 2

    SUB = "ise"
    ENT = "en_vip"
    CATEGORY = "read_sentence"
    TEXT = '\uFEFF' + str(text)

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
                        v1[0, 0] = (int(float(sentence.attrib["total_score"])) + 1) * 20
                        v1[0, 1] = (int(float(sentence.attrib["integrity_score"])) + 1) * 20
                        v1[0, 2] = (int(float(sentence.attrib["fluency_score"])) + 1) * 20
                        v1[0, 3] = (int(float(sentence.attrib["standard_score"])) + 1) * 20
                        v1[0, 4] = (int(float(sentence.attrib["accuracy_score"])) + 1) * 20
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



def picture(user_id,article_id,paragraph_id,data):
    matplotlib.use('Agg')
    # 数据和标签

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
    master_path = f"D:/Apache24/www/images/"
    dir_path = f"{master_path}" + f"{user_id}_{article_id}_{paragraph_id}.png"

    # 保存雷达图到本地文件
    plt.savefig(dir_path, bbox_inches='tight', dpi=300)
    # 关闭图形，避免在 Jupyter Notebook 中显示
    plt.close()
    dir_path_url = "http://10.135.116.43:8080/images/"
    url = dir_path_url + f"{user_id}_{article_id}_{paragraph_id}.png"
    return url


# 转换格式，返回地址【1】
def change_audio(input_audio_file_mp3, article_id,paragraph_id):

    # 加载音频文件
    audio = AudioSegment.from_file(input_audio_file_mp3)
    # 转换为单声道
    audio = audio.set_channels(1)
    # 设置采样率为 16000Hz
    audio = audio.set_frame_rate(16000)
    # 导出为16位 PCM WAV
    output_audio_file_m4a = ""
    dir_path = "D:/Apache24/www/users_audios/m4a/"
    output_audio_file_m4a = f"{dir_path}" + f"{article_id}_{paragraph_id}.m4a"
    audio.export(output_audio_file_m4a, format="mp4")
    return output_audio_file_m4a


def search_by_keyword(keyword):
    search_result = []
    # 连接到数据库
    conn = mysql.connector.connect(
        host = host_mysql,
        user = user_mysql,
        password = password_mysql,
        database = database_mysql
    )
    cursor = conn.cursor()

    # 处理用户输入
    keyword = keyword.strip().lower()


    # 执行模糊查询
    query = "SELECT article_id FROM articles WHERE title LIKE %s"
    search_string = "%{}%".format(keyword)
    #print(search_string)
    cursor.execute(query,[search_string])
    results = cursor.fetchall()

    #print(type(results))
    #print(results)

    for result in results:
        search_result.append(result[0])

    # 关闭数据库连接
    cursor.close()
    conn.close()

    return search_result


# 获取用户画像
def get_user_features(user_id):
    user_feature = []
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
        cursor.execute(
            f'SELECT life,work,recreation,travel,sport,technology FROM user_portrait WHERE student_id = {user_id}')
        rows = cursor.fetchall()
        #print(rows)
        if len(rows) > 0:
            for row in rows[0]:
                user_feature.append(row)
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    # return 1
    return user_feature

def get_article_features():
    article_id = []
    article_features = []
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
        cursor.execute(f'SELECT category,likes,page_view FROM articles')
        rows1 = cursor.fetchall()

        for row in rows1:
            article_features.append(row)

        cursor = connection.cursor()
        cursor.execute(f'SELECT article_id FROM articles')
        rows2 = cursor.fetchall()

        for row in rows2:
            article_id.append(row)

        cursor = connection.cursor()
        cursor.execute(f'SELECT content FROM articles')
        rows3 = cursor.fetchall()

        for row in rows3:
            article_content.append(row)


    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return article_id, article_features

# 获取推荐文章内容,批量，接收列表
def get_article_content(article_id):
    result = []

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
        for i in range(len(article_id)):
            cursor.execute(f"SELECT article_id,title,category,content,likes,page_view,release_time,image  FROM articles WHERE article_id = {int(article_id[i])}")
            rows = cursor.fetchall()
            result.append(rows)

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return result

# 增加浏览量
def increase_page_views(article_id):
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
        update_query = "UPDATE articles SET page_view = page_view + 1 WHERE  article_id = %s"
        cursor.execute(update_query, [article_id])
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return Response(-1)

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return 1


def increae_user_read_num(user_id,category_id):

    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysql,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        categorys = {0:"life", 1:"travel", 3:"technology",2:"recreation", 4:"work", 5:"sport"}
        cursor = connection.cursor()
        # 执行查询
        query = "SELECT EXISTS (SELECT 1 FROM user_portrait WHERE student_id = %s)"
        cursor.execute(query, (user_id,))
        flag = cursor.fetchone()[0]
        print(category_id)
        print(categorys[int(category_id)])
        print("------------------------------------------------")
        if flag == 1:

            try:
                update_query = "UPDATE user_portrait SET {column} = {column} + 1 WHERE student_id = %s"

                formatted_query = update_query.format(column=categorys[int(category_id)])
                cursor.execute(formatted_query, [user_id])
            except  Exception as e:
                print(f"update query error when user_portrait: {e}")
        if flag == 0:
            print("###########################################")
            insert_query = "INSERT INTO user_portrait (life, travel,technology, recreation, work, sport) VALUES (%s, %s, %s,%s,%s,%s)"
            # 要插入的数据
            data = [0,0,0,0,0,0]
            data[int(category_id)] = 1
            # 执行 SQL 语句
            cursor.execute(insert_query, data)
        connection.commit()
    except Exception as err:
        print(f"Error: {err}.f{category_id}")
        return Response(-1)
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return 1



# 将音频文件转换为二进制字符串【1】
def encode_audio_to_base64_string(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        # 读取音频文件的二进制数据
        binary_data = audio_file.read()
        # 使用 base64 编码二进制数据
        base64_encoded_data = base64.b64encode(binary_data)
        # 将编码后的数据转换为字符串
        base64_string = base64_encoded_data.decode('utf-8')
        return base64_string



