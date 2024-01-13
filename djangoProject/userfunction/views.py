import copy
import csv
from datetime import datetime

import bcrypt
import matplotlib
from django.http import JsonResponse
from django.shortcuts import render
from matplotlib import pyplot as plt
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

#from inster import write_Data

host_mysql = HOST
user_mysqy = USER
password_mysql = PASSWORD
database_mysql = DATABASE


#打卡功能逻辑
'''
1. 用户切换试图，进入打卡界面，发送请求,服务器端识别，返回用户历史打卡记录
2 .用户于打卡界面请求打卡，并传输参数：checkin_data, user_id(还是账户后期修改)
    2.1 服务器检查用户打卡日期是否相符；
        2.1.1 相符返回1，并将打卡记录添加进数据库
        2.1.2 不符返回0，结束
'''

# 查询用户历史打卡记录返回
@api_view(['GET'])
def return_history_checkin_record(request):
    user_id = request.query_params.get('user_id')
    date_checkined = []
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        query = "SELECT  check_in_time FROM check_in_record WHERE user_id = %s"
        cursor.execute(query,[user_id])
        rows = cursor.fetchall()

        print(type(rows))

        for row in rows:
            print(row[0])
            date = {}
            # 使用 strftime 将日期时间对象格式化为仅包含年月日的字符串
            formatted_date = row[0].strftime("%Y-%m-%d")
            date["date"] = formatted_date
            date_checkined.append(date)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(date_checkined)

@api_view(['GET'])
def checkin(request):
    user_id = request.query_params.get('user_id')
    date_check_in = request.query_params.get('date_check_in')

    print(user_id)
    print(date_check_in)

    # 将日期字符串转换为 datetime 对象
    date_object = datetime.strptime(date_check_in, "%Y-%m-%d")
    # 获取当前日期和时间
    current_datetime = datetime.now()
    # 比较年、月、日是否相同
    if (date_object.year == current_datetime.year and
            date_object.month == current_datetime.month and
            date_object.day == current_datetime.day):
        # 检查当天是否签到，没有的话加入一条记录
        flag = insert_checkin_record(user_id)
        if flag == 1:
            return Response(1) # 修改，返回所有记录
        else:
            return Response(-1)
    else:
        return Response(-1)


def insert_checkin_record(user_id):
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        insert_query = """INSERT INTO check_in_record (user_id) VALUES (%s)"""
        cursor.execute(insert_query, [user_id])
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return 1





'''
用户活跃度排行榜【20】
1. 要求：
    - 包括用户阅读总篇数
    - 包括用户阅读句子个数
2. 实现：
    2.1 用户阅读数，查询：user_portrait
    2.2 阅读句子个数，查询表grade_record
'''

# 无参数传递
@api_view(['GET'])
def activity_ranking(request):

    read_article_num = get_read_article_num()
    read_sentence_num = get_read_sentence_num()
    print("read_article_num:",read_article_num)
    print("read_sentence_num:",read_sentence_num)
    merged_dict = copy.deepcopy(read_sentence_num)
    print("merged_dict:",merged_dict)
    for key, value in read_article_num.items():
        if key in read_sentence_num:
            read_sentence_num[key] += value  # 如果键相同，相加值
        else:
            read_sentence_num[key] = value  # 否则，添加新的键值对

    activity_ranking_dict_sorted = sorted(merged_dict.items(), key=lambda x: x[1], reverse=True)

    rank_list =  return_user_info(activity_ranking_dict_sorted)

    print(merged_dict)

    print(read_article_num)
    print(read_sentence_num)

    return   Response(rank_list)


def return_user_info(activity_ranking_dict_sorted):
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        query = "SELECT student_id, name FROM student"
        cursor.execute(query)
        rows = cursor.fetchall()
        rows_dict = {}
        for row in rows:
            #print(1)
            #print(row)
            rows_dict[row[0]] = row[1]

        print(rows_dict)


        return_user_info_list = []

        i = 1

        for row in activity_ranking_dict_sorted:
            l = {}
            #print("k")
            print(row)
            l["id"] = row[0]
            l["score"] = row[1]
            l["name"] = rows_dict[row[0]]
            l["rank"] = i
            i = i + 1
            return_user_info_list.append(l)

        print(return_user_info_list)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return return_user_info_list

@api_view(['GET'])
def return_user_info_personal(request):

    user_id = request.query_params.get('user_id')
    return_user_info_dict = {}
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        query = "SELECT name,gender,class_id,grade,faculty FROM student where student_id = %s"
        cursor.execute(query,[user_id])
        rows = cursor.fetchall()
        for row in rows:
            #print(1)
            #print(row)
            if row[0] is None:
                return_user_info_dict["name"] = "null"
            else:
                return_user_info_dict["name"] = row[0]
            if row[1] is None:
                return_user_info_dict["gender"] = "null"
            else:
                return_user_info_dict["gender"] = row[1]
            if row[2] is None:
                return_user_info_dict["class_id"] = "null"
            else:
                return_user_info_dict["class_id"] = row[2]
            if row[3] is None:
                return_user_info_dict["grade"] = "null"
            else:
                return_user_info_dict["grade"] = row[3]
            if row[4] is None:
                return_user_info_dict["faculty"] = "null"
            else:
                return_user_info_dict["faculty"] = row[4]

        print(return_user_info_dict)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(return_user_info_dict)


@api_view(['GET'])
def update_user_info(request):
    user_id = request.query_params.get('user_id')
    user_name = request.query_params.get('user_name')
    #user_password = request.query_params.get('user_password')
    user_gender = request.query_params.get('user_gender')
    user_class = request.query_params.get('user_class')
    user_grade = request.query_params.get('user_grade')
    user_faculty = request.query_params.get('user_faculty')
    #user_avatar = request.query_params.get('user_avatar')
    user_password = ""
    user_password_bytes = bytes(user_password, "utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(user_password_bytes, salt)

    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        sql = """UPDATE student SET name = %s, class_id = %s, grade = %s,faculty = %s, gender = %s WHERE student_id = %s"""
        cursor.execute(sql, (user_name, user_class, user_grade, user_faculty,user_gender,user_id))
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return Response(-1)
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(1)


# 荣誉榜单
@api_view(['get'])
def rake_user_info(request):
    user_id = request.query_params.get('user_id')
    read_article_num = get_read_article_num()
    read_sentence_num = get_read_sentence_num()
    merged_dict = copy.deepcopy(read_sentence_num)
    for key, value in read_article_num.items():
        if key in read_sentence_num:
            read_sentence_num[key] += value  # 如果键相同，相加值
        else:
            read_sentence_num[key] = value  # 否则，添加新的键值对

    activity_ranking_dict_sorted = sorted(merged_dict.items(), key=lambda x: x[1], reverse=True)
    rakes = return_user_info(activity_ranking_dict_sorted)
    print(1)
    print(activity_ranking_dict_sorted)
    for rake in rakes:
        print(rake)
        print(rake['id'])
        if rake['id'] == int(user_id):
            rake_user = rake
            return Response(rake_user)
    return Response(-1)


def user_num():
    users_list = []

    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        query = "SELECT student_id FROM student"
        cursor.execute(query)
        rows = cursor.fetchall()

        # print(rows[0])
        # print(type(rows))

        # flag = True

        for row in rows:
            # if flag == True:
            #     print(flag)
            #     flag = False
            users_list.append(row[0])


    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()

    return users_list

def get_read_article_num():
    user_articles_list = {}
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()

        # SQL 查询语句
        query = f"SELECT * FROM user_portrait"
        # 执行查询

        cursor.execute(query)

        rows = cursor.fetchall()

        for row in rows:
            user_articles_list[row[0]]=row[1]+ row[2]+ row[3]+ row[4]+ row[5] + row[6]
        # print(user_articles_list)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return  user_articles_list


def get_read_sentence_num():
    user_sentence_list = {}
    users_list = user_num()
    # print(users_list)
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()

        # 根据 user_ids 的长度创建相应数量的占位符
        placeholders = ', '.join(['%s'] * len(users_list))

        # SQL 查询语句
        query = f"SELECT student_id, COUNT(*) as record_count FROM grade_record WHERE student_id IN ({placeholders}) GROUP BY student_id"

        # 执行查询
        cursor.execute(query, users_list)
        rows = cursor.fetchall()

        rows_list = []
        for row in rows:
            user_sentence_list[row[0]] = row[1]
        # print(rows_list)
        # print(user_sentence_list)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return user_sentence_list



'''
1. 该功能需统计用户打卡、阅读以及朗读文章的条目
2. 设定荣誉获取的门限：
    2.1 大于20点亮一个；大于40点亮两个，大于80点亮3个；大于160点亮四个
3. 统计数目：
    3.1 对于打卡：统计check_in_record
    3.2 对于阅读：统计user_portrait
    3.3 对于朗读：统计grade_record
'''
@api_view(['GET'])
def honor_rank(request):
    user_id = request.query_params.get('user_id')
    year = request.query_params.get('year')

    # 返回列表
    check_in_num_returned = []
    read_article_num_returned = []
    read_sentence_num_returned = []

    return_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    checkin_num = get_sigleuser_chech_in_record_num(user_id)
    readarticle_num = get_sigleuser_read_article_num(user_id)
    readsentence_num = get_sigleuser_read_sentence_num(user_id)

    if checkin_num >= 2 and checkin_num < 40:
        # check_in_num_returned = [1,0,0]
        return_list[6] = 1
        return_list[7] = 0
        return_list[8] = 0
    elif checkin_num >= 40 and checkin_num < 80:
        return_list[6] = 1
        return_list[7] = 1
        return_list[8] = 0
    elif checkin_num >= 80:
        return_list[6] = 1
        return_list[7] = 1
        return_list[8] = 1
    else:
        return_list[6] = 0
        return_list[7] = 0
        return_list[8] = 0

    if readarticle_num >= 2 and readarticle_num < 40:
        return_list[0] = 1
        return_list[1] = 0
        return_list[2] = 0
    elif readarticle_num >= 40 and readarticle_num < 80:
        return_list[0] = 1
        return_list[1] = 1
        return_list[2] = 0
    elif readarticle_num >= 80:
        return_list[0] = 1
        return_list[1] = 1
        return_list[2] = 1
    else:
        return_list[0] = 0
        return_list[1] = 0
        return_list[2] = 0


    if readsentence_num >= 2 and readsentence_num < 40:
        return_list[3] = 1
        return_list[4] = 0
        return_list[5] = 0
    elif readsentence_num >= 40 and readsentence_num < 80:
        return_list[3] = 1
        return_list[4] = 1
        return_list[5] = 0
    elif readsentence_num >= 80:
        return_list[3] = 1
        return_list[4] = 1
        return_list[5] = 1
    else:
        return_list[3] = 0
        return_list[4] = 0
        return_list[5] = 0


    month_num = get_check_year_month_num(user_id,year)
    print(month_num)

    for i in range(0,12):
        if month_num[i] < 1 :
            return_list[i+9] = 0
        else:
            return_list[i+9] = 1


    print(read_article_num_returned)
    print(read_sentence_num_returned)
    print(check_in_num_returned)
    print(len(return_list))

    return_dict = {}
    return_dict["article_rank1"] = return_list[0]
    return_dict["article_rank2"] = return_list[1]
    return_dict["article_rank3"] = return_list[2]
    return_dict["sentence_rank1"] = return_list[3]
    return_dict["sentence_rank2"] = return_list[4]
    return_dict["sentence_rank3"] = return_list[5]
    return_dict["check_in_rank1"] = return_list[6]
    return_dict["check_in_rank2"] = return_list[7]
    return_dict["check_in_rank3"] = return_list[8]
    return_dict["January"] = return_list[9]
    return_dict["February"] = return_list[10]
    return_dict["March"] = return_list[11]
    return_dict["April"] = return_list[12]
    return_dict["May"] = return_list[13]
    return_dict["June"] = return_list[14]
    return_dict["July"] = return_list[15]
    return_dict["August"] = return_list[16]
    return_dict["September"] = return_list[17]
    return_dict["October"] = return_list[18]
    return_dict["November"] = return_list[19]
    return_dict["December"] = return_list[20]



    print(return_list)
    print(return_dict)
    print("**********************************************************************")
    print(return_dict)

    return  Response(return_dict)

# 统计打卡
def get_sigleuser_chech_in_record_num(user_id):
    num = 0
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()

        # 编写 SQL 查询命令
        sql = "SELECT COUNT(*) FROM check_in_record WHERE user_id = %s"
        # 执行 SQL 命令
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        num = rows[0][0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return num

# 统计阅读
def get_sigleuser_read_article_num(user_id):
    num = 0
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()

        # SQL 查询语句
        query = f"SELECT * FROM user_portrait where student_id = %s"
        # 执行查询
        cursor.execute(query,(user_id,))
        rows = cursor.fetchall()
        if len(rows) > 0:
            print(rows)
            num = rows[0][1]+ rows[0][2]+ rows[0][3]+ rows[0][4]+ rows[0][5] + rows[0][6]
        # print(user_articles_list)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return num

# 统计朗读
def get_sigleuser_read_sentence_num(user_id):
    num = 0
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()

        # SQL 查询语句
        sql = "SELECT COUNT(*) FROM grade_record WHERE student_id = %s"

        # 执行查询
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()

        nums = rows[0][0]
        # print(rows_list)
        # print(user_sentence_list)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return num


# 打卡月榜统计
def get_check_year_month_num(user_id,year):
    month_num = [0,0,0,0,0,0,0,0,0,0,0,0]
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        query = """SELECT YEAR(check_in_time) AS year, MONTH(check_in_time) AS month, COUNT(*) AS count FROM check_in_record WHERE user_id = %s AND YEAR(check_in_time) = %s GROUP BY YEAR(check_in_time), MONTH(check_in_time) ORDER BY month;"""
        # 执行查询
        cursor.execute(query, (user_id,year))  # 假设 user_id 为 1
        # 获取查询结果
        results = cursor.fetchall()

        for row in results:
            month_num[row[1]-1] = row[2]

        print(month_num)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return -1
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return month_num

# @api_view(['GET'])
# def data_insert(request):
#     write_Data()
#     return Response(1)



@api_view(['GET'])
def picture_personal(request):
    user_id = request.query_params.get('user_id')
    return_dict = {}
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        cursor = connection.cursor()
        # SQL 查询语句
        query = f"SELECT life,work, recreation, travel, sport, technology from user_portrait where student_id = %s"

        # 执行查询
        cursor.execute(query, [user_id])
        rows = cursor.fetchall()
        print(rows)
        rows_article_list = []
        for row in rows[0]:
            rows_article_list.append(row)

        print(rows_article_list)
        url_pie = draw_pie_chart(rows_article_list,user_id)
        query = f"SELECT grade,time from grade_record where student_id = %s"
        cursor.execute(query, [user_id])
        rows = cursor.fetchall()
        rows_score_dict = {}
        for row in rows:
            date = row[1]
            rows_score_dict[str(date)] = row[0]

        print(rows_score_dict)
        url_line = draw_line_chart(rows_score_dict,user_id)

        return_dict["url_pie"] = url_pie
        return_dict["url_line"] = url_line


    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return_dict["url_pie"] = "null"
        return_dict["url_line"] = "null"
        return Response()
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return Response(return_dict)




def draw_pie_chart(data,user_id):
    """
    绘制一个饼状图，显示提供的数据。
    :param data: 包含六个维度的数据列表。
    """
    matplotlib.use('Agg')
    # 确保数据有六个维度
    if len(data) != 6:
        raise ValueError("数据列表必须包含六个维度")
    labels = ["life","work", "recreation", "travel", "sport", "technology"]

    # 饼图的颜色
    colors = ['yellowgreen', 'gold', 'lightskyblue', 'lightcoral', 'darkorange', 'pink']
    # 绘制饼图
    plt.figure(figsize=(10, 8))
    # plt.pie(data, labels=labels, colors=colors,
    #         autopct='%1.1f%%', shadow=True, startangle=140)

    plt.pie(data, labels=labels, autopct='%1.1f%%', colors=colors,startangle=140, shadow=False)

    #plt.pie(data, labels=labels, autopct='%1.1f%%')
    plt.axis('equal')  # 确保饼图是圆的
    # 添加标题
    plt.title('Reader-Record Chart')



    master_path = "D:/Apache24/www/images/"
    dir_path = f"{master_path}" + f"{user_id}_pie.png"
    # 保存雷达图到本地文件
    plt.savefig(dir_path, bbox_inches='tight', dpi=300)
    # 关闭图形，避免在 Jupyter Notebook 中显示
    plt.close()
    dir_path_url = "http://10.135.116.43:8080/images/"
    url = dir_path_url + f"{user_id}_pie.png"
    return url

def draw_line_chart(data_dict,user_id):
    """
    绘制一个折线图，显示提供的数据。
    :param data_dict: 一个字典，其中键是字符串形式的时间戳，值是数值。
    """
    # 解析时间和数值
    matplotlib.use('Agg')

    sorted_time_dict = dict(sorted(data_dict.items(), key=lambda item: item[0]))

    print(sorted_time_dict)

    times = [datetime.fromisoformat(key) for key in data_dict]
    values = [data_dict[key] for key in data_dict]

    # 对时间进行排序（如果需要）
    sorted_indices = sorted(range(len(times)), key=lambda k: times[k])
    times_sorted = [times[i] for i in sorted_indices]
    values_sorted = [values[i] for i in sorted_indices]
    print("----------------------------------------------------------")
    print(times_sorted)
    print(values_sorted)
    print("----------------------------------------------------------")
    # 绘制折线图

    x_data = []

    for i in range(1,len(times_sorted)+1):
        x_data.append(i)

    plt.plot(x_data, values_sorted, marker='o')  # 'o' 表示点
    plt.xlabel('time')
    plt.ylabel('score')
    plt.title('time-score')
    plt.xticks(rotation=45)  # 旋转标签以便阅读
    plt.tight_layout()  # 调整布局
    # 添加标题
    plt.title('Time-Score Chart')
    master_path = "D:/Apache24/www/images/"
    dir_path = f"{master_path}" + f"{user_id}_line.png"
    # 保存雷达图到本地文件
    plt.savefig(dir_path, bbox_inches='tight', dpi=300)
    # 关闭图形，避免在 Jupyter Notebook 中显示
    plt.close()
    dir_path_url = "http://10.135.116.43:8080/images/"
    url = dir_path_url + f"{user_id}_line.png"
    return url

