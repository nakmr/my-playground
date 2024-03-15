import anthropic
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    client = anthropic.Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    message = client.messages.create(
        model=os.getenv("CLAUDE_MODEL"),
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "こんにちは、Claude！"}
        ]
    )

    print(message.content[0].text)


if __name__ == "__main__":
    main()
