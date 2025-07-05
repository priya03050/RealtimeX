from ast import parse
import socket
import select
from requestHandler import handle_request

from requestHandler import handle_request
import websocketFrame
TCP_IP = '127.0.0.1'
TCP_PORT = 5006
BUFFER_SIZE = 1024 * 1024

DEFAULT_HTTP_RESPONSE = (
    b'''<HTML><HEAD><meta http-equiv="content-type" content="text/html;charset=utf-8">\r\n
<TITLE>200 OK</TITLE></HEAD><BODY>\r\n
<H1>200 OK</H1>\r\n
Welcome to the default.\r\n
</BODY></HTML>\r\n\r\n''')

def main():
    tcp_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    # Creates a TCP socket (IPv4, stream-oriented).
    tcp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    # Allows the socket to reuse the address without waiting for timeout after a restart.
    tcp_socket.bind((TCP_IP,TCP_PORT))
    # Binds the socket to 127.0.0.1:5006.
    tcp_socket.listen(1)
    # Starts listening for connections (backlog size of 1).
    print('Listening on port:',TCP_PORT)
    input_sockets = [tcp_socket]
    output_sockets = []
    xlist = []
    # Keeps track of the sockets to monitor. Initially only the main listening socket.

    ws_sockets = []

    while(True):
        readable_sockets = select.select(input_sockets,output_sockets,xlist,5)[0]
        # Waits (up to 5 seconds) for any socket in input_sockets to become readable.

        for ready_socket in readable_sockets:
            if(ready_socket.fileno() == -1):
                # skips sockets that have been closed (fileno() == -1).
                continue
            if(ready_socket == tcp_socket):
                 # If the main server socket is ready, it means there's a new incoming connection.
                 print('Handling main door socket')
                 handle_new_connection(tcp_socket,input_sockets)

            elif ready_socket in ws_sockets:
                print('this is where we would handle the websocket message')
                handle_websocket_message(ready_socket, input_sockets,
                                         ws_sockets)
            else:
                 # it's a client socket sending data.
                 print('Handling regular socket read')
                 handle_request(ready_socket,input_sockets,ws_sockets)


def handle_new_connection(main_door_socket, input_sockets):
     client_socket, client_addr = main_door_socket.accept()
     print("New socket",client_socket.fileno(),'from address:', client_addr)
     input_sockets.append(client_socket)


def handle_websocket_message(client_socket, input_sockets,ws_sockets):
    data_in_bytes = client_socket.recv(BUFFER_SIZE)

    websocket_frame = websocketFrame.WebsocketFrame()
    websocket_frame.populateFromWebsocketFrameMessage(data_in_bytes)

    payload = websocket_frame.get_payload_data()

    try:
        decoded_msg = payload.decode('utf-8')
        print('Received message:', decoded_msg)
    except UnicodeDecodeError:
        print('Received binary or invalid message.')
        return

    # Construct WebSocket text frame to broadcast (simple, no masking)
    frame = b'\x81' + bytes([len(payload)]) + payload

    broadcast_message(client_socket, ws_sockets, frame)
    return      

def broadcast_message(sender_socket, ws_sockets, message_bytes):
    for ws_sock in ws_sockets:
        if ws_sock != sender_socket:
            try:
                ws_sock.sendall(message_bytes)
            except Exception as e:
                print(f"Failed to send to socket {ws_sock.fileno()}: {e}")
                # close_socket(ws_sock, input_sockets=[], ws_sockets=ws_sockets)


if __name__ == '__main__':
    main()     

          
    