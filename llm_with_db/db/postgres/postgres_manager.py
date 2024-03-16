import os

import psycopg2

def call_postgres():
    HOST = os.getenv('PG_HOST')
    USER = os.getenv('PG_USER')
    PASSWORD = os.getenv('PG_PASSWORD')
    PORT = os.getenv('PG_PORT')
    DB_NAME = os.getenv('PG_DATABASE')

    database_url = f"host={HOST} port={PORT} dbname={DB_NAME} user={USER} password={PASSWORD}"
    conn = psycopg2.connect(database_url)
    print("Connected to PostgreSQL")
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS inventory")
    print("Finished dropping table (if existed)")

    cursor.execute("CREATE TABLE inventory (id serial PRIMARY KEY, name VARCHAR(50), quantity INTEGER);")
    print("Finished creating table")

    cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("banana", 150))
    cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("orange", 154))
    cursor.execute("INSERT INTO inventory (name, quantity) VALUES (%s, %s);", ("apple", 100))
    print("Inserted 3 rows of data")

    cursor.execute("SELECT * FROM inventory;")
    rows = cursor.fetchall()

    for row in rows:
        print("Data row = (%s, %s, %s)" % (str(row[0]), str(row[1]), str(row[2])))

    conn.commit()
    cursor.close()
    conn.close()


