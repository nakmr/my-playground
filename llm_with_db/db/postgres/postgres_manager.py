# -*- coding: utf-8 -*-
"""

PostgreSQLとの接続およびデータの操作を行うモジュール。

"""
import os

import psycopg2


def get_connection() -> psycopg2.connect:
    """

    PostgreSQLとの接続を取得する。

    Returns: psycopg2.connectオブジェクト。

    """
    HOST = os.getenv('PG_HOST')
    USER = os.getenv('PG_USER')
    PASSWORD = os.getenv('PG_PASSWORD')
    PORT = os.getenv('PG_PORT')
    DB_NAME = os.getenv('PG_DATABASE')

    # Connect to DB
    database_url = f"host={HOST} port={PORT} dbname={DB_NAME} user={USER} password={PASSWORD}"
    return psycopg2.connect(database_url)


def add_thread_info(thread) -> None:
    """

    会話Threadの情報（Thread ID、ユーザID）を登録する。

    Args:
        thread: ConversationThreadオブジェクト

    Returns: None

    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Create table
            CREATE_TABLE_QUERY = f"""
                CREATE TABLE IF NOT EXISTS thread_info (
                    thread_id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50),
                    thread_embedding vector(1536) 
                );"""
            cur.execute(CREATE_TABLE_QUERY)

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
            cur.execute(INSERT_THREAD_INFO_QUERY)

        conn.commit()


def message_embedding_with_azureai_extension(thread) -> None:
    """

    ConversationThreadオブジェクトからmessagesを取得して、embeddingする。
    embeddingにはAzure Database for PostgreSQLの拡張機能`azure_ai`を利用する。
    この拡張機能を利用する場合、embeddingする文字列にシングルクォーテーションがあると、embeddingに失敗することに注意。

    Args:
        thread: ConversationThreadオブジェクト

    Returns: None

    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert embeddings
            INSERT_EMBEDDING = f"""
                UPDATE thread_info
                SET thread_embedding = azure_openai.create_embeddings('{os.getenv("AOAI_EMBEDDING_MODEL")}', '{str(thread.messages)}')
                WHERE thread_id = '{thread.id}';
            """
            cur.execute(INSERT_EMBEDDING)

            # Create HNSW index
            CREATE_HNSM_INDEX = """
                CREATE INDEX ON conference_session_embeddings USING hnsw (session_embedding vector_ip_ops);
            """
            cur.execute(CREATE_HNSM_INDEX)

        conn.commit()


def message_embedding(thread) -> None:
    """

    ConversationThreadオブジェクトからmessagesを取得して、embeddingする。
    embeddingにはAzure OpenAIを利用する。

    Args:
        thread: ConversationThreadオブジェクト

    Returns: None

    """
    # Message embedding
    response = thread.llm_client.embeddings.create(
        model=os.getenv("AOAI_EMBEDDING_MODEL"),
        input=str(thread.messages)
    )
    embedded_message = response.data[0].embedding

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert embeddings
            UPDATE_EMBEDDING = f"""
                UPDATE thread_info
                SET thread_embedding = '{embedded_message}'
                WHERE thread_id = '{thread.id}';
            """
            cur.execute(UPDATE_EMBEDDING)

            # Create HNSW index
            CREATE_HNSM_INDEX = """
                CREATE INDEX ON conference_session_embeddings USING hnsw (session_embedding vector_ip_ops)
            """
            cur.execute(CREATE_HNSM_INDEX)

        conn.commit()
