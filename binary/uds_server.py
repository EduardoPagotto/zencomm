import asyncio
import os
import struct

UDS_PATH = "/tmp/uds_socket"

async def handle_client(reader, writer):
    addr = writer.get_extra_info('sockname')
    print(f"Accepted connection from {addr}")

    try:
        while True:
            # Read header: 4 bytes for data length
            header = await reader.readexactly(4)
            data_len = struct.unpack('>I', header)[0]

            # Read binary data
            data = await reader.readexactly(data_len)
            print(f"Received from {addr}: {data.hex()}")

            # Echo back the data
            writer.write(header + data)
            await writer.drain()

    except asyncio.IncompleteReadError:
        print(f"Client {addr} disconnected.")
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Connection with {addr} closed.")

async def main():
    if os.path.exists(UDS_PATH):
        os.remove(UDS_PATH)

    server = await asyncio.start_unix_server(handle_client, UDS_PATH)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
