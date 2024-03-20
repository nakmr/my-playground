import json
import os
import threading
import time

from dotenv import load_dotenv
from openai import OpenAI

from llm_user_interupt.chat_agent import ChatAgent
from prompt.controller import prompt3, prompt4, prompt5, prompt2, prompt1

chathistory: ChatAgent = ChatAgent()
game_running: bool = False


def _get_client():
    load_dotenv()

    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )


def chat_with_assistant(
        query: str,
        temperature: float = 0.0,
        history=None
) -> str:
    client = _get_client()

    if query != "":
        try:
            if history is not None and type(history) is list:
                if query.startswith("システム："):
                    sp_query = [
                        s for s in query.split("\n\n") if s.strip() != ""
                    ]
                    if len(sp_query) == 1:
                        history.append({
                            "role": "system",
                            "content": query
                        })
                    else:
                        history.append({
                            "role": "system",
                            "content": sp_query[0]
                        })
                        for usr_query in sp_query[1:]:
                            history.append({
                                "role": "user",
                                "content": usr_query
                            })
                else:
                    history.append({
                        "role": "user",
                        "content": query
                    })
                messages = history
            else:
                messages = [{
                    "role": "user",
                    "content": query
                }]

            response = client.chat.completions.create(
                model=os.getenv("CHAT_MODEL_GPT35"),
                messages=messages,
                temperature=temperature
            )

            answer = response.choices[0].message.content

            if history is not None and type(history) is list:
                history.append({
                    "role": "assistant",
                    "content": answer
                })

            print(f"{query} ===> {answer}")
            return answer

        except:
            pass

    return ""


def intervention():
    historydata = chathistory.customer
    # フラグを戻す
    delivery = chathistory.delivery
    chathistory.delivery = None
    chathistory.num_star = None
    chathistory.clerk = []
    chathistory.customer = []

    prompt = prompt3 % delivery
    # システムの発言（お客の回答）：クッキーの枚数が正しかったか
    clerk_answer = chat_with_assistant(prompt, 0.8, historydata)
    # システムの発言（お客の回答）：お店の評価を求める
    clerk_answer = chat_with_assistant(prompt4, 0.8, historydata)
    # システムの発言（お客の回答）：お店の評価をJSONで出力
    clerk_answer = chat_with_assistant(prompt5, 0.8, historydata)

    jsonstr = chathistory.get_json_from_response(clerk_answer)
    try:
        jsondata = json.loads(jsonstr)
        if type(jsondata) is dict and "num_star" in jsondata and type(jsondata["num_star"]) is int:
            return jsondata["num_star"]
        else:
            return None
    except:
        return None


def chat_with_agent():
    global chathistory, game_running

    # Start
    clerk_prompt = prompt1
    customer_prompt = prompt2

    while game_running:
        customer_answer = chathistory.get_message(
            chat_with_assistant(clerk_prompt, 0.8, chathistory.customer)
        )

        if chathistory.delivery is not None:  # ユーザからの干渉あり
            return intervention()

        prompt = f"{customer_prompt}お客：「{customer_answer}」"
        clerk_answer = chathistory.get_message(
            chat_with_assistant(prompt, 0.8, chathistory.clerk)
        )

        if chathistory.delivery is not None:  # ユーザからの干渉あり
            return intervention()

        customer_prompt = ""
        clerk_prompt = f"店員：「{clerk_answer}」"


def repeat_chat():
    global chathistory, game_running

    while game_running:
        nstar = chat_with_agent()
        if nstar is not None:
            chathistory.num_star = nstar
            while chathistory.num_star is not None:
                time.sleep(0.1)


def start_chat_with_agent():
    control_thread = threading.Thread(target=repeat_chat())
    control_thread.setDaemon(True)
    control_thread.start()
