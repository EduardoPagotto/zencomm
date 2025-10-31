# uds_client.py
import asyncio
import os

UDS_PATH = "/tmp/my_uds_socket"

async def uds_client(message):
    reader, writer = await asyncio.open_unix_connection(path=UDS_PATH)
    print("Connecting to UDS.")

    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    response = data.decode().strip()
    print(f"Received via UDS: {response}")

    await asyncio.sleep(20)

    print("Closing UDS connection.")
    writer.close()
    await writer.wait_closed()

async def main_uds_client():
    await asyncio.gather(
        uds_client("UDS Message 1"),
        uds_client("UDS Message 2"),
        uds_client("UDS Message 3")
    )

if __name__ == "__main__":
    asyncio.run(main_uds_client())
