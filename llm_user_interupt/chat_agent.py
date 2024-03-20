import json



class ChatAgent:
    def __init__(self):
        self.clerk = []
        self.customer = []
        self.delivery = None
        self.num_star = None

    def get_message(self, answer) -> str:
        answer = answer.replace("「", "").replace("」", "")
        sp = None

        if ":" in answer:
            sp = answer.split(":")
        if "：" in answer:
            sp = answer.split("：")
        if sp is not None:
            answer = sp[1] if sp[0] != "システム" else ""

        return answer.strip()

    def get_json_from_response(self, response: str) -> str:
        try:
            json.loads(response)
            return response
        except:
            if "```" in response:
                code = response[response.index("```") + 3:]
                if "```" in code:
                    code = code[:code.index("```")]
                if code.startswith("json"):
                    code = code[len("json")]
                elif code.startswith("\n"):  # Markdown記法における言語コードなしのコードブロック
                    pass
                else:
                    return ""

                return code.strip()
            return response


