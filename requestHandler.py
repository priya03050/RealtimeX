from keyGenerator import generate_sec_websocket_accept
from validator import is_valid_ws_handshake_request


WS_ENDPOINT = '/websocket'
BUFFER_SIZE = 1024 * 1024

DEFAULT_HTTP_RESPONSE = (
    b'''<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">\r\n
<TITLE>200 OK</TITLE></HEAD><BODY>\r\n
<H1>200 OK</H1>\r\n
Welcome to the default.\r\n
</BODY></HTML>\r\n\r\n''')



def handle_request(client_socket, input_sockets, ws_sockets):
    print('Handling request from client socket 1:', client_socket.fileno())
    message = ''

    while True:
        data_in_bytes = client_socket.recv(BUFFER_SIZE)
    
        if len(data_in_bytes) == 0:
            close_socket(client_socket, input_sockets, ws_sockets)
            return
        message_segment = data_in_bytes.decode()
        message += message_segment
        if (len(message) > 4 and message_segment[-4:] == '\r\n\r\n'):
            break

    print('Received message:')
    print(message)

    (method, target, http_version, headers_map) = parse_request(message)

    print('method, target, http_version:', method, target, http_version)
    print('headers:')
    print(headers_map)

    if target == WS_ENDPOINT:
        print('request to ws endpoint!')
        if is_valid_ws_handshake_request(method,
                                         http_version,
                                         headers_map):
            handle_ws_handshake_request(
                client_socket,
                ws_sockets,
                headers_map)
            return
        else:
            # Invalid WS request.
            print('debug 2')
            client_socket.send(b'HTTP/1.1 400 Bad Request')
            close_socket(client_socket, input_sockets, ws_sockets)
            return

    print('debug 3')
    client_socket.send(b'HTTP/1.1 200 OK\r\n\r\n' + DEFAULT_HTTP_RESPONSE)
    close_socket(client_socket, input_sockets, ws_sockets)  
        

def handle_ws_handshake_request(
        client_socket,
        ws_sockets,
        headers_map):
    print('debug 1')
    ws_sockets.append(client_socket)
    sec_websocket_accept_value = generate_sec_websocket_accept(
        headers_map.get('sec-websocket-key')
    )
    websocket_response = ''
    websocket_response += 'HTTP/1.1 101 Switching Protocols\r\n'
    websocket_response += 'Upgrade: websocket\r\n'
    websocket_response += 'Connection: Upgrade\r\n'
    websocket_response += (
        'Sec-Websocket-Accept: '+ sec_websocket_accept_value.decode()+'\r\n'
    )
    websocket_response += '\r\n'
    print('\nresponse:\n', websocket_response)
    client_socket.send(websocket_response.encode())


def close_socket(client_socket, input_sockets, ws_sockets):
    print('closing socket')
    if client_socket in ws_sockets:
        ws_sockets.remove(client_socket)
    input_sockets.remove(client_socket)
    client_socket.close()
    return


def parse_request(request):
     headers_map = {}

     split_request = request.split('\r\n\r\n')[0].split('\r\n')
     [method, target, http_version] = split_request[0].split(' ')
     headers = split_request[1:]
     for header_entry in headers :
          [header, value] = header_entry.split(': ')
          headers_map[header.lower()] = value
     return (method, target, http_version, headers_map)


