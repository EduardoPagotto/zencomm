from urllib.parse import urlparse

#url = 'tcp://192.168.0.1:5000'
# Scheme: tcp
# Network Location (netloc): 192.168.0.1:5000
# Path:
# Parameters:
# Query:
# Fragment:
# Hostname: 192.168.0.1
# Port: 5000

#url = 'udp://./tmp/sockt0'
# Scheme: udp
# Network Location (netloc): .
# Path: /tmp/sockt0
# Parameters:
# Query:
# Fragment:
# Hostname: .
# Port: None

#url = 'udp:///tmp/sockt0'
# Scheme: udp
# Network Location (netloc):
# Path: /tmp/sockt0
# Parameters:
# Query:
# Fragment:
# Hostname: None
# Port: None


# url = "http://www.example.com:8080/path/to/resource?param1=value1&param2=value2#fragment"

# parsed_url = urlparse(url)

# print(f"Scheme: {parsed_url.scheme}")
# print(f"Network Location (netloc): {parsed_url.netloc}")
# print(f"Path: {parsed_url.path}")
# print(f"Parameters: {parsed_url.params}") # Note: params are often embedded in the path
# print(f"Query: {parsed_url.query}")
# print(f"Fragment: {parsed_url.fragment}")
# print(f"Hostname: {parsed_url.hostname}")
# print(f"Port: {parsed_url.port}")


import asyncio
import os

async def connect_with_timeout(unix_socket_path, timeout):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_unix_connection(path=unix_socket_path),
            timeout=timeout
        )
        print(f"Successfully connected to {unix_socket_path}")
        # Perform operations with reader and writer
        writer.close()
        await writer.wait_closed()
        return reader, writer
    except asyncio.TimeoutError:
        print(f"Connection to {unix_socket_path} timed out after {timeout} seconds.")
        return None, None
    except FileNotFoundError:
        print(f"Unix socket not found at {unix_socket_path}")
        return None, None
    except ConnectionRefusedError:
        print(f"Connection to {unix_socket_path} refused.")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

async def main():
    # Create a dummy Unix socket file for demonstration
    unix_socket_path = "/tmp/my_unix_socket"

    # Simulate a server that takes a long time to accept connections
    async def dummy_server():
        server = await asyncio.start_unix_server(
            lambda r, w: None, # No-op client_connected_cb
            path=unix_socket_path
        )
        print(f"Dummy server listening on {unix_socket_path}")
        try:
            await asyncio.sleep(10) # Simulate a long running server
        finally:
            server.close()
            await server.wait_closed()
            if os.path.exists(unix_socket_path):
                os.remove(unix_socket_path)

    # Start the dummy server in the background
    server_task = asyncio.create_task(dummy_server())

    # Attempt to connect with a timeout
    reader, writer = await connect_with_timeout(unix_socket_path, timeout=2)

    # Wait for the server task to complete (or be cancelled by the main loop ending)
    await server_task

if __name__ == "__main__":
    asyncio.run(main())
