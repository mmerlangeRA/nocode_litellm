import openai
import uvicorn
import asyncio
import pydantic
import traceback
from ChatBot import ChatBot
from CancelToken import CancelToken
from custom_schemas import ChatResponse, ChatRequest
from ConnectionManager import ConnectionManager
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from websockets.exceptions import ConnectionClosedOK
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, status, HTTPException

origins = ['*']
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server_tasks = []
connection_manager = ConnectionManager()


@app.on_event("shutdown")
async def shutdown_event():
    await connection_manager.disconnect_all()

    tasks = {task for task in server_tasks if task != asyncio.current_task()}
    if len(tasks) > 1:
        print(f'Cancelling {len(tasks)} task(s).')
        [task.cancel() for task in tasks]


@app.post("/chat/get_answer")
async def get_answer(response: Response, request: ChatRequest):
    server_task = asyncio.current_task()
    server_tasks.append(server_task)

    class StreamingError(Exception):
        pass

    async def stream_chat_response(query: str):
        buffer = []
        cancel_token = CancelToken()
        chatbot = ChatBot()

        try:
            async for token, user_query in chatbot.chat(user_query=query, cancel_token=cancel_token):
                if token is None:
                    continue
                buffer.append(token)
                yield token

            answer = ''.join(buffer)
            print(f"got answer: \n{answer}")

        except StopAsyncIteration:
            print("got stop async iteration")
            cancel_token.cancel()
            return
        except Exception as e:
            print(f"error in streaming:")
            raise StreamingError(f"An error occurred while streaming: {e}")

    try:
        user_query = request.query
        print(f"got user query: {user_query}")

        return StreamingResponse(stream_chat_response(user_query), media_type="text/plain")

    except StreamingError as e:
        print(f"error in streaming: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}
    except HTTPException as e:
        print(f"http exception error in streaming: {str(e)}")
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e)}
    except Exception as e:
        print(f"unexpected error in streaming: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}


@app.websocket("/chat/{user_id}")
async def chat_endpoint(websocket: WebSocket, user_id: str):
    server_task = asyncio.current_task()
    server_tasks.append(server_task)

    cancel_token = None
    websocket_conn_established = False

    try:
        await connection_manager.connect(websocket, user_id)
        print(f"connection accepted to websocket from: {user_id}")
        websocket_conn_established = True

    except Exception:
        print(f"error in accepting websocket connection from : {user_id}")
        print(traceback.format_exc())
        await websocket.close()
        print("closed websocket")

    send_task = None

    async def handle_incoming_messages():
        nonlocal send_task
        nonlocal cancel_token

        cancel_token = CancelToken()
        user_input = None
        while True:
            try:
                user_input = await websocket.receive_json()

                valid_input = False

                try:
                    user_input = ChatRequest(**user_input)
                    valid_input = True

                except (pydantic.error_wrappers.ValidationError, ValueError) as e:
                    resp = ChatResponse(
                        sender="bot",
                        message=f"{str(e)}.Invalid input. Try again.",
                        type="error",
                        user_id=user_id,
                        user_query=user_input.query
                    )
                    print("invalid input")
                    await websocket.send_json(resp.dict())

                stop_generating = False
                if valid_input:
                    stop_generating = user_input.stop_generating

                if stop_generating is False and valid_input:
                    print(f"got input from user: {user_input.dict()}")
                    cancel_token = CancelToken()
                    print("cancel token reset")

                    question = user_input.query

                    async def send_tokens():
                        try:
                            print("send tokens started...")
                            counter = 0
                            buffer = []
                            generator_finished = False

                            chatbot = ChatBot()

                            try:
                                async for token, user_query in chatbot.chat(user_query=question,
                                                                            cancel_token=cancel_token):

                                    if token is None:
                                        continue

                                    resp = ChatResponse(sender="bot", message=token, type="stream",
                                                        user_id=user_id, user_query=user_query)
                                    await connection_manager.send_json(message=resp.dict(), websocket=websocket)
                                    counter += 1
                                    buffer.append(token)

                                generator_finished = True

                            except asyncio.CancelledError:
                                print("send tokens cancelled")
                                pass

                            if generator_finished:
                                buffer_str = "".join(buffer)
                                finished_generating_answer = True
                                if cancel_token:
                                    if cancel_token.is_cancelled is True:
                                        finished_generating_answer = False

                                    elif cancel_token.is_cancelled is False:
                                        finished_generating_answer = True

                                print(f"bot response: {buffer_str}")

                                end_resp = ChatResponse(sender="bot", message="", type="end", user_id=user_id,
                                                        )
                                await websocket.send_json(end_resp.dict())

                        except Exception:
                            print(f"error for user id: {user_id}")
                            print(traceback.format_exc())
                            resp = ChatResponse(
                                sender="bot",
                                message="Sorry, something went wrong. Try again later.",
                                type="error",
                                user_id=user_id,
                                user_query=user_input.query
                            )
                            await websocket.send_json(resp.dict())

                        except openai.error.RateLimitError:
                            print(f"user {user_id} rate limit exceeded")
                            resp = ChatResponse(
                                sender="bot",
                                message="Rate limit exceeded, please try after some time",
                                type="error",
                                user_id=user_id,
                                user_query=user_input.query
                            )
                            await websocket.send_json(resp.dict())
                            await websocket.close()
                            await connection_manager.disconnect(user_id)

                        except (asyncio.exceptions.TimeoutError, openai.error.Timeout):
                            print(f"timeout error for user id: {user_id}")
                            resp = ChatResponse(
                                sender="bot",
                                message="Sorry, request timed out. Try again.",
                                type="error",
                                user_id=user_id,
                                user_query=user_input.query
                            )
                            await websocket.send_json(resp.dict())
                            await connection_manager.disconnect(user_id)

                    send_task = asyncio.create_task(send_tokens())
                    await asyncio.sleep(0)  # force the running of send_task

                if stop_generating:
                    print("received stop generation signal")
                    if send_task and not send_task.done():
                        cancel_token.cancel()
                        print("token cancelled")
                        send_task.cancel()

                    end_resp = ChatResponse(sender="bot", message="", type="end", user_id=user_id,
                                            )
                    await websocket.send_json(end_resp.dict())

            except (asyncio.exceptions.TimeoutError, openai.error.Timeout):
                print(f"timeout error for user id: {user_id}")
                resp = ChatResponse(
                    sender="bot",
                    message="Sorry, request timed out. Try again.",
                    type="error",
                    user_id=user_id,
                    user_query=user_input.query if hasattr(user_input, "query") else ""
                )
                await websocket.send_json(resp.dict())
                await websocket.close()
                await connection_manager.disconnect(user_id)

            except WebSocketDisconnect:

                await connection_manager.disconnect(user_id)
                print(f"websocket disconnect for user_id: {user_id}")
                break

            except ConnectionClosedOK:
                pass

            except Exception:
                print(f"error for user id: {user_id}")
                resp = ChatResponse(
                    sender="bot",
                    message="Sorry, something went wrong. Try again later.",
                    type="error",
                    user_id=user_id,
                    user_query=user_input.query if hasattr(user_input, "query") else ""
                )
                await websocket.send_json(resp.dict())
                # await websocket.close()
                # await connection_manager.disconnect(user_id)

            finally:
                print("*" * 100)
                print("\n")

    receive_task = None
    if websocket_conn_established:
        try:
            receive_task = asyncio.create_task(handle_incoming_messages())
            await asyncio.sleep(0)
            await asyncio.shield(receive_task)
        except asyncio.CancelledError:
            if send_task and not send_task.done():
                send_task.cancel()

            if receive_task and not receive_task.done():
                receive_task.cancel()


if __name__ == '__main__':
    uvicorn.run('main_app:app', host="localhost", port=5002, reload=False, workers=1)