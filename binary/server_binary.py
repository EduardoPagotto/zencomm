import asyncio
import os
import struct

# Define a simple binary message format:
# 4 bytes for message length (unsigned int) + actual binary data
HEADER_FORMAT = "!I"  # Network byte order, unsigned int

async def handle_client(reader, writer):
    """
    Handles a single client connection, receiving and echoing binary data.
    """
    peername = writer.get_extra_info('peername')
    print(f"Client connected: {peername}")

    try:
        while True:
            # Read the header to get the length of the incoming message
            header_data = await reader.readexactly(struct.calcsize(HEADER_FORMAT))
            if not header_data:
                break  # Connection closed

            message_length = struct.unpack(HEADER_FORMAT, header_data)[0]

            # Read the actual binary data
            data = await reader.readexactly(message_length)
            print(f"Received {len(data)} bytes from {peername}: {data[:20]}...") # Print first 20 bytes for brevity

            # Echo the data back to the client
            writer.write(header_data + data)
            await writer.drain()

    except asyncio.IncompleteReadError:
        print(f"Client {peername} disconnected unexpectedly.")
    except ConnectionResetError:
        print(f"Client {peername} forcibly closed the connection.")
    except Exception as e:
        print(f"Error with client {peername}: {e}")
    finally:
        print(f"Closing connection with {peername}")
        writer.close()
        await writer.wait_closed()

async def main_tcp(host, port):
    """
    Starts an asyncio TCP server.
    """
    server = await asyncio.start_server(handle_client, host, port)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()

async def main_uds(path):
    """
    Starts an asyncio Unix Domain Socket server.
    """
    if os.path.exists(path):
        os.remove(path)  # Clean up previous socket file if it exists

    server = await asyncio.start_unix_server(handle_client, path)
    print(f"Serving on UDS: {path}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    SERVER_TYPE = "TCP"  # Change to "UDS" to use Unix Domain Sockets

    if SERVER_TYPE == "TCP":
        HOST = "127.0.0.1"
        PORT = 8888
        asyncio.run(main_tcp(HOST, PORT))
    elif SERVER_TYPE == "UDS":
        UDS_PATH = "/tmp/my_uds_socket"
        asyncio.run(main_uds(UDS_PATH))
    else:
        print("Invalid SERVER_TYPE. Choose 'TCP' or 'UDS'.")
