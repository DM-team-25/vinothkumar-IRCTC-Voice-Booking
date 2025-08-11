'''Title       : V_IRCTC(Voice based Ticket Booking)
Author         : VINOTHKUMAR
Created at     : VINOTHKUMAR
Updated at     :
Reviewed by    :
Reviewed At:                 '''



import pymysql

def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Aspire@123",
        database="V_IRCTC",
        connect_timeout=5
    )

