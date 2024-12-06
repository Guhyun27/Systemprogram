import mysql.connector


# sql db접속 함수
def get_db_connection():
    connection = mysql.connector.connect(
        host="14.47.163.184",
        user="admin",  # MySQL 사용자 이름
        password="1234",  # MySQL 사용자 비밀번호
        database="sys",  # 데이터베이스 이름
    )
    return connection
