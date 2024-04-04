import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                query = input("enter query: ")
                async with session.post(

                        'http://localhost:5002/chat/get_answer',
                        json={
                                'query': query,

                              }
                ) as response:

                    # Ensure the request was successful
                    if response.status == 200:

                        # Asynchronously read the streamed response
                        async for line in response.content:
                            print(line.decode('utf-8'), end='')

                    else:
                        print(f"Received unexpected status code {response.status}")
            except KeyboardInterrupt:
                await session.close()
                break

            finally:
                print("\n")
                print("*" * 100)
                print("\n")


# Run the event loop
if __name__ == '__main__':
    asyncio.run(main())