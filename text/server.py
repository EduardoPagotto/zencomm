# uds_server.py
import asyncio
import os

UDS_PATH = "/tmp/my_uds_socket"

async def handle_uds_client(reader, writer):
    # For UDS, peername might be less descriptive, but you still get a writer object
    print("Accepted UDS connection.")

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode().strip()
            print(f"Received via UDS: {message}")

            response = f"UDS Echo: {message}"
            writer.write(response.encode())
            await writer.drain()
    except asyncio.CancelledError:
        print("UDS client connection cancelled.")
    finally:
        print("Closing UDS connection.")
        writer.close()
        await writer.wait_closed()

async def main_uds_server():
    # Clean up previous socket file if it exists
    if os.path.exists(UDS_PATH):
        os.remove(UDS_PATH)

    server = await asyncio.start_unix_server(
        handle_uds_client, path=UDS_PATH
    )
    print(f"Serving on UDS path: {UDS_PATH}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main_uds_server())
