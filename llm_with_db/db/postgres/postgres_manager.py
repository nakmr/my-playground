import os

import psycopg2


def add_thread_info(thread):
    HOST = os.getenv('PG_HOST')
    USER = os.getenv('PG_USER')
    PASSWORD = os.getenv('PG_PASSWORD')
    PORT = os.getenv('PG_PORT')
    DB_NAME = os.getenv('PG_DATABASE')

    # Connect to DB
    database_url = f"host={HOST} port={PORT} dbname={DB_NAME} user={USER} password={PASSWORD}"
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS thread_info")

    # Create table
    CREATE_TABLE_QUERY = f"""
        CREATE TABLE thread_info (
            thread_id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50),
            thread_embedding vector(1536)
        );"""
    cursor.execute(CREATE_TABLE_QUERY)

    # Insert thread info
    INSERT_THREAD_INFO_QUERY = f"""
        INSERT INTO thread_info (
            thread_id, user_id
        )
        VALUES (
            '{thread.id}',
            '{thread.user_id}'
        )
    """
    cursor.execute(INSERT_THREAD_INFO_QUERY)

    conn.commit()
    cursor.close()
    conn.close()



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

    cursor.execute("DELETE FROM inventory WHERE name = %s;", ("orange",))
    print("Deleted 1 row of data")

    conn.commit()
    cursor.close()
    conn.close()


def call_postgres_embedding():
    HOST = os.getenv('PG_HOST')
    USER = os.getenv('PG_USER')
    PASSWORD = os.getenv('PG_PASSWORD')
    PORT = os.getenv('PG_PORT')
    DB_NAME = os.getenv('PG_DATABASE')

    database_url = f"host={HOST} port={PORT} dbname={DB_NAME} user={USER} password={PASSWORD}"
    conn = psycopg2.connect(database_url)
    print("Connected to PostgreSQL")
    cursor = conn.cursor()

    # Clean up existing tables
    cursor.execute("DROP TABLE IF EXISTS conference_session_embeddings;")
    cursor.execute("DROP TABLE IF EXISTS conference_sessions;")

    # Create tables
    CREATE_TABLE_CONF_SESSIONS = """
    CREATE TABLE conference_sessions(
        session_id int PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
        title text,
        session_abstract text,
        duration_minutes integer,
        publish_date timestamp
    );
    """
    cursor.execute(CREATE_TABLE_CONF_SESSIONS)

    CREATE_TABLE_CONF_SESSION_EMBEDDINGS = """
    CREATE TABLE conference_session_embeddings(
       session_id integer NOT NULL REFERENCES conference_sessions(session_id),
       session_embedding vector(1536)
);
    """
    cursor.execute(CREATE_TABLE_CONF_SESSION_EMBEDDINGS)

    # Insert data
    INSERT_TABLE_CONF_SESSIONS = """
    INSERT INTO conference_sessions(
        title,
        session_abstract,
        duration_minutes,
        publish_date
    ) 
    VALUES
        (
            'Gen AI with Azure Database for PostgreSQL flexible server',
            'Learn about building intelligent applications with azure_ai extension and pg_vector',
            60,
            current_timestamp
        ),
        (
            'LLMを利用したアプリケーション開発',
            'LLMを利用したアプリケーション開発について、その勘所について共有する',
            60,
            current_timestamp
        ),
        (
            'Deep Dive: PostgreSQL database storage engine internals',
            ' We will dig deep into storage internals',
            30,
            current_timestamp
        );
    """
    cursor.execute(INSERT_TABLE_CONF_SESSIONS)

    # Get embedding for the session abstract
    # GET_EMBEDDING = f"""
    # SELECT pg_typeof(
    #     azure_openai.create_embeddings(
    #         '{os.getenv("AOAI_EMBEDDING_MODEL")}', c.session_abstract)
    #     ) as embedding_data_type,
    #     azure_openai.create_embeddings('{os.getenv("AOAI_EMBEDDING_MODEL")}', c.session_abstract)
    # FROM
    #     conference_sessions AS c
    # LIMIT 10;
    # """
    # cursor.execute(GET_EMBEDDING)
    # rows = cursor.fetchall()

    # Insert embeddings
    INSERT_EMBEDDING = f"""
        INSERT INTO conference_session_embeddings(
            session_id,
            session_embedding
        )
        SELECT
            c.session_id,
            (
                azure_openai.create_embeddings('{os.getenv("AOAI_EMBEDDING_MODEL")}', c.session_abstract)
            )
        FROM conference_sessions AS c
        LEFT OUTER JOIN conference_session_embeddings AS e ON e.session_id = c.session_id
        WHERE e.session_id IS NULL;
    """
    cursor.execute(INSERT_EMBEDDING)

    # Create HNSW index
    CREATE_HNSM_INDEX = """
        CREATE INDEX ON conference_session_embeddings USING hnsw (session_embedding vector_ip_ops)
    """
    cursor.execute(CREATE_HNSM_INDEX)

    SELECT_EMBEDDING_DATA = f"""
    SELECT c.*,
        -- <＝>: calcurate cosine distance
        -- <#>: calcurate inner product
        (e.session_embedding <#> azure_openai.create_embeddings('{os.getenv("AOAI_EMBEDDING_MODEL")}','Session to learn about building chatbots')::vector) * -1 AS similarity
    FROM conference_session_embeddings e
    INNER JOIN conference_sessions c ON c.session_id = e.session_id
    ORDER BY similarity
    LIMIT 5;
    """
    cursor.execute(SELECT_EMBEDDING_DATA)
    rows = cursor.fetchall()

    print(rows)

    conn.commit()
    cursor.close()
    conn.close()
