import asyncio
import struct
import random

UDS_PATH = "/tmp/uds_socket"

async def send_receive_data(data_to_send):
    try:
        reader, writer = await asyncio.open_unix_connection(UDS_PATH)
        print(f"Connected to UDS server at {UDS_PATH}")

        # Pack data length as a 4-byte unsigned integer (big-endian)
        header = struct.pack('>I', len(data_to_send))
        writer.write(header + data_to_send)
        await writer.drain()
        print(f"Sent: {data_to_send.hex()}")

        # Read echoed header and data
        received_header = await reader.readexactly(4)
        received_data_len = struct.unpack('>I', received_header)[0]
        received_data = await reader.readexactly(received_data_len)
        print(f"Received: {received_data.hex()}")

        writer.close()
        await writer.wait_closed()
        print("Connection closed.")

    except ConnectionRefusedError:
        print(f"Connection refused. Is the server running at {UDS_PATH}?")
    except FileNotFoundError:
        print(f"UDS socket not found at {UDS_PATH}. Is the server running?")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    # Send some random binary data
    for i in range(3):
        data = os.urandom(random.randint(10, 50)) # Random length binary data
        await send_receive_data(data)
        await asyncio.sleep(0.5) # Simulate some delay

if __name__ == "__main__":
    asyncio.run(main())
