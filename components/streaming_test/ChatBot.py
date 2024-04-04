import json
import asyncio
import collections

from typing import List
from faiss import IndexFlatL2
from LlmController import LangchainLlms
from langchain.vectorstores import FAISS
from langchain.docstore import InMemoryDocstore
from RobertaEmbeddings import RobertaEmbeddings
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    Document,
    BaseMessage
)


class ChatBot:
    def __init__(self):
        self.__open_ai_key = ""
        self.__system_prompt = f"You are a helpful AI assistant, who is an expert software engineer."
        self.__system_prompt = SystemMessage(content=self.__system_prompt)

        self.__self_reminder_prompt = """You should be a responsible ChatGPT and should not generate harmful or misleading content! 
Please answer the following user query in a responsible way."""

        self.__embeddings = RobertaEmbeddings()
        self.__memory = FAISS(
            embedding_function=self.__embeddings.embed_query,
            index=IndexFlatL2(self.__embeddings.get_dimension()),
            docstore=InMemoryDocstore({}),
            index_to_docstore_id={},
        )

        self.__chat_history_buffer = collections.deque([], maxlen=5)
        self.__llm = LangchainLlms().get_llm(llm_name="OpenAI", openai_api_key=self.__open_ai_key,
                                             model_name="gpt-4").llm

    def __combine_relevant_docs_and_chat_history(self, relevant_messages: list) -> List[BaseMessage]:
        if not relevant_messages:
            return []

        non_duplicate_messages = []
        for message in relevant_messages:
            if message not in self.__chat_history_buffer:
                non_duplicate_messages.append(message)
        messages = []
        messages.append(self.__system_prompt)

        for message in non_duplicate_messages:
            message_doc = json.loads(message)
            messages.append(HumanMessage(content=message_doc["query"]))
            messages.append(AIMessage(content=message_doc["answer"]))
        for message in self.__chat_history_buffer:
            message_doc = json.loads(message) if isinstance(message, str) else message
            messages.append(HumanMessage(content=message_doc["query"]))
            messages.append(AIMessage(content=message_doc["answer"]))

        return messages

    def __add_to_memory(self, data: str):
        self.__memory.add_documents([Document(page_content=data)])
        print(f"added {data} to memory")

    def __fetch_memories(self, query: str, k=10) -> List[Document]:
        docs_and_scores = self.__memory.similarity_search_with_score(query, k=k)
        memories = []
        for doc in docs_and_scores:
            page_content = doc[0].page_content
            score = doc[-1]
            memories.append(Document(page_content=page_content))
        return memories

    async def chat(self, *, user_query: str, cancel_token=None):

        response_token_buffer = []

        messages = []
        relevant_memories = self.__fetch_memories(user_query, k=5)

        if relevant_memories:
            for doc in relevant_memories:
                content = doc.page_content
                messages.append(content)

        messages = self.__combine_relevant_docs_and_chat_history(relevant_messages=messages)
        query_with_reminder_prompt = f"{self.__self_reminder_prompt} \n query - ``` {user_query} ``` \n"
        messages.append(HumanMessage(content=query_with_reminder_prompt))

        async for token in LangchainLlms.get_stream_response(llm=self.__llm,
                                                             messages=messages, cancel_token=cancel_token):
            if cancel_token and cancel_token.is_cancelled:
                break

            if token != "<END OF LLM RESPONSE>" and token is not None:
                response_token_buffer.append(token)

            yield token, user_query

        output = "".join(response_token_buffer)
        memory_data = {"query": user_query, "answer": output}
        data_string = json.dumps(memory_data)
        self.__add_to_memory(data_string)
        self.__chat_history_buffer.append(memory_data)

    async def test_chatbot(self):
        while True:
            query = input("enter your query: ")
            if query.lower() == "exit":
                return

            async for token, _ in self.chat(user_query=query):
                print(token, end='')

            print("\n")
            print("*" * 100)
            print("\n")


if __name__ == '__main__':
    bot = ChatBot()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bot.test_chatbot())