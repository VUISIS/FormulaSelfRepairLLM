from langchain.memory import ConversationBufferMemory

class SingletonMemory:
    _instance = None
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SingletonMemory, cls).__new__(cls)
        return cls._instance

    def get_memory(self):
        return self.memory