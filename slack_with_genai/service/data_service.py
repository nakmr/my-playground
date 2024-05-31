import psycopg2
import os

def get_db_connection():
    """データベース接続を取得する"""
    return psycopg2.connect(
        dbname=os.getenv("PG_DB_NAME"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        # sslmode = "require"
    )

def insert_thread_mapping(thread_ts, conversation_id):
    check_query = '''
    SELECT conversation_id 
    FROM slack_dify_threads 
    WHERE thread_ts = %s;
    '''

    insert_query = '''
    INSERT INTO slack_dify_threads (thread_ts, conversation_id) 
    VALUES (%s, %s)
    ON CONFLICT (thread_ts) DO NOTHING;
    '''

    update_query = '''
    UPDATE slack_dify_threads 
    SET conversation_id = %s 
    WHERE thread_ts = %s;
    '''
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # 既存のconversation_idを確認
                cur.execute(check_query, (thread_ts,))
                result = cur.fetchone()
                
                if result:
                    existing_conversation_id = result[0]
                    if not existing_conversation_id:
                        # 既存のconversation_idが空の場合、更新
                        cur.execute(update_query, (conversation_id, thread_ts))
                else:
                    # 新しい行を挿入
                    cur.execute(insert_query, (thread_ts, conversation_id))
                
                conn.commit()
    except Exception as error:
        print(f"Error inserting data: {error}")

def get_conversation_id(thread_ts):
    select_query = '''
    SELECT conversation_id 
    FROM slack_dify_threads 
    WHERE thread_ts = %s;
    '''
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(select_query, (thread_ts,))
                result = cur.fetchone()
                if result:
                    return result[0]
                else:
                    return None
    except Exception as error:
        print(f"Error fetching data: {error}")
        return None
