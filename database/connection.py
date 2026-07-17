import mysql.connector

def get_connection(): 
    connection = mysql.connector.connect(
        host="localhost", 
        user="root", 
        password="@Stargirl456",
        database="texas_food_insecurity"
    )

    return connection 


