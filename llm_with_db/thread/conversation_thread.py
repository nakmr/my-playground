import uuid
from openai import AzureOpenAI
import os

class ConversationThread:
    """

    1ThreadごとのIDやメッセージを管理するオブジェクト。

    Attributes:
        id (UUID): Thread1つずつに割り当てられるUUID
        user_id (str): ユーザID
        messages (list): メッセージを集約したList
        llm_client: LLMのクライアントオブジェクト

    """
    def __init__(self):
        self.id = uuid.uuid4()
        self.user_id = "user_temp"
        self.messages: list
        self.llm_client = _get_llm_client()

def _get_llm_client() -> AzureOpenAI:
    """

    Azure OpenAI オブジェクトを取得する。

    Returns: AzureOpenAIオブジェクト

    """
    return AzureOpenAI(
        azure_endpoint=os.getenv("AOAI_ENDPOINT"),
        api_key=os.getenv("AOAI_API_KEY"),
        api_version=os.getenv("AOAI_API_VERSION")
    )
