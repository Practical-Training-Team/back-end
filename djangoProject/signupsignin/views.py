from django.shortcuts import render

# Create your views here.

from rest_framework.response import Response
from rest_framework.decorators import api_view
import mysql.connector
import bcrypt
from server import HOST, USER, PASSWORD, DATABASE

host_mysql = HOST
user_mysql = USER
password_mysql = PASSWORD
database_mysql = DATABASE


# 全局变量，记录用户账户列表
account_list = []
#【ok】
@api_view(['GET'])
def signup(request):
    # 标志变量
    flag1 = True

    account = request.query_params.get('account')
    password = request.query_params.get('password')

    # 判断参数是否为空
    if account is None or account.strip() == '':
        return Response(-1)

    if password is None or password.strip() == '':
        return Response(-1)

    # 判断账户是否重复
    flag, account_list = read_AccountList()
    if flag == False:
        return Response(-1)

    for accounted in account_list:
        if account == accounted:
            return Response(-1)
    # 判断密码安全强度

    # 密码hash
    bpassword = bytes(password,'utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(bpassword, salt)

    # 更新数据库
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
        insert_query = """INSERT INTO student (account,password_hashed) VALUES (%s, %s)"""
        data = (account, hashed)
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
            return Response(1)

    return Response(1)

@api_view(['GET'])
def signin(request):
    login_account = request.query_params.get('login_account')
    login_password = request.query_params.get('login_password')

    # 判断参数是否合法
    if login_account is None or len(login_account) == 0:
        return Response(-1)

    # 判断是否已注册

    flag, account_list = read_AccountList()
    if not flag:
        return Response(-1)
    flag1 = False
    for account in account_list:
        if account == login_account:
            flag1 = True
            break

    if flag1 == True:
        password, f2 = read_Password(login_account)
        user_id, f3 = read_UserID(login_account)

        if not f2 or not f3:
            return Response(-1)
    else:
        return Response(-1)

    # 判断密码正确与否
    login_password = login_password.strip()
    byt_ps = bytes(login_password, "utf-8")

    if bcrypt.checkpw(byt_ps, password):
        f2 = increase_student_sign_in(login_account)  # 增加學生登入次數
        if not f2:
            return Response(-1)
        else:
            return Response(user_id)
    else:
        return Response(-1)


# 读取已注册用户列表
def read_AccountList():
    flag = True
    account_list = []
    connection = None
    cursor = None
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
        query = 'SELECT account FROM student'
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            account_list.append(row[0])  # 假设只需要第一个字段
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flag = False
    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
    return flag, account_list  # 返回标志和账户列表


# 读取当前用户用户密码
def read_Password(login_account):
    flag = True
    user_password = ""
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysql,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")
        # 返回当前登录用户密码
        cursor = connection.cursor()
        query = "SELECT password_hashed FROM student WHERE account=%s"
        cursor.execute(query, (login_account,))
        rows1 = cursor.fetchall()


        user_password = bytes(rows1[0][0], "utf-8")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return user_password, flag


# 读取当前登录用户ID
def read_UserID(login_account):
    user_id = -1
    flag = True
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
        query = "SELECT (student_id) FROM student WHERE account = %s"
        cursor.execute(query,[login_account])
        rows = cursor.fetchall()
        user_id = rows[0][0]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        flag = False

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return user_id, flag




def increase_student_sign_in(account):
    flag = True
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
        query = "update student set sign_in_num = sign_in_num+1 where account = %s"
        cursor.execute(query,[account])
        print("增加登录次数")
        # 提交更改
        connection.commit()

    except mysql.connector.Error as err:
        flag = False
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
    return flag

