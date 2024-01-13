import csv
import mysql.connector
import server

host_mysql = server.HOST
user_mysqy = server.USER
password_mysql = server.PASSWORD
database_mysql = server.DATABASE

def write_Data():
    tuples_list = []
    dir_path = "D:\\MyData\\Data\\QQFile"
    try:
        connection = mysql.connector.connect(
            host=host_mysql,
            user=user_mysqy,
            password=password_mysql,
            database=database_mysql
        )
        if connection.is_connected():
            print("成功连接到MySQL数据库")

        # 打开 CSV 文件并读取内容
        with open(f'{dir_path}\\trains_sentence.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                # 将每一行转换为元组，并添加到列表中
                tuples_list.append(tuple(row))
        # 删除列表中的第一个元组
        if tuples_list:
            tuples_list.pop(0)

        print(tuples_list[0:5])


        for tuples in tuples_list:
            cursor = connection.cursor()
            #insert_query = """INSERT INTO student (name,class,faculty,grade,password_hashed,account) VALUES (%s, %s, %s, %s, %s, %s)"""
            insert_query = """INSERT INTO sentence (content,category) VALUES (%s,%s)"""
            #insert_query = """INSERT INTO articles (title,content,image,category) VALUES (%s,%s,%s,%s)"""
            data = (tuples[0], tuples[1])
            cursor.execute(insert_query, data)
            connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # 关闭连接
        if 'connection' in locals() and connection.is_connected():
            connection.close()
