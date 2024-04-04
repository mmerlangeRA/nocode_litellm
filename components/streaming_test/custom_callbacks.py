import asyncio

from uuid import UUID
from langchain.schema import LLMResult
from typing import List, Any, Optional
from langchain.callbacks.base import AsyncCallbackHandler


class MyAsyncQueueCallbackHandler(AsyncCallbackHandler):
    """ callback handler where you can pass a queue and receive the tokens over the queue"""
    def __init__(self, queue: asyncio.Queue, cancel_token=None):
        self.__queue = queue
        self.__cancel_token = cancel_token
        self.__buffer = []

    def get_buffer_contents(self):
        return "".join(self.__buffer)

    def reset_buffer(self):
        self.__buffer = []

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if self.__cancel_token and self.__cancel_token.is_cancelled is True:
            raise asyncio.CancelledError

        if token is not None:
            self.__buffer.append(token)
            await self.__queue.put(token)

    async def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> None:
        await self.__queue.put("<END OF LLM RESPONSE>")