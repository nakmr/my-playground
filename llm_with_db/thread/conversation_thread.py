import uuid


class ConversationThread:
    def __init__(self):
        self.id = uuid.uuid4()
        self.user_id = "user_temp"
