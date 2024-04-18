import psycopg2

class ConnectionPostgres:
    def __init__(self, dbname, user, password, host, port) -> None:
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def fetch_data(self, query):
        with psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
    
    def insert_data(self, query, data):
        with psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, data)
        connection.commit()

    def update_data(self, query, params):
        with psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                connection.commit()

postgres = ConnectionPostgres(
    dbname="exam_p1",
    user="postgres",
    password="090090815",
    host="localhost",
    port="5432"
)
