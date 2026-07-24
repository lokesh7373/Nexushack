import socket, json

def receive_full_response(sock, buffer_size=16384):
    """Receive the complete response, potentially in multiple chunks"""
    chunks = []
    sock.settimeout(200.0)
    try:
        while True:
            try:
                # print("Waiting for data from Isaac")
                #time.sleep(0.5)
                chunk = sock.recv(buffer_size)
                if not chunk:
                    # If we get an empty chunk, the connection might be closed
                    if not chunks:  # If we haven't received anything yet, this is an error
                        raise Exception("Connection closed before receiving any data")
                    break
                
                chunks.append(chunk)
                
                # Check if we've received a complete JSON object
                try:
                    data = b''.join(chunks)
                    json.loads(data.decode('utf-8'))
                    # If we get here, it parsed successfully
                    # print(f"Received complete response ({len(data)} bytes)")
                    return json.loads(data.decode('utf-8'))
                except json.JSONDecodeError:
                    # Incomplete JSON, continue receiving
                    continue
            except socket.timeout:
                 # If we hit a timeout during receiving, break the loop and try to use what we have
                # print("Socket timeout during chunked receive")
                break

            except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                # print(f"Socket connection error during receive: {str(e)}")
                raise  # Re-raise to be handled by the caller
    except socket.timeout:
        print("Socket timeout during chunked receive")
    except Exception as e:
        print(f"Error during receive: {str(e)}")
        raise
        
    # If we get here, we either timed out or broke out of the loop
    # Try to use what we have
    if chunks:
        data = b''.join(chunks)
        # print(f"Returning data after receive completion ({len(data)} bytes)")
        try:
            # Try to parse what we have
            json.loads(data.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            # If we can't parse it, it's incomplete
            raise Exception("Incomplete JSON response received")
    else:
        raise Exception("No data received")