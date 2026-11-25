import socket
import threading
import json

HOST = '0.0.0.0'
PORT = 9999

connected_clients = []
connected_clients_conn = {}

def handle_client(conn, addr):
        print(f"[NEW CONNECTION] {addr} connected!")
        client_name = None                                       
        with conn:
            try:                                                   
                while True:
                    raw_data = conn.recv(1024)
                    if not raw_data:
                        break                                      

                    try:
                        json_string = raw_data.decode('utf-8')

                        data_dict = json.loads(json_string)
                        client_name = data_dict.get("clientName")  

                        if (data_dict.get("type") == "JOIN"):
                            if data_dict.get("clientName") in connected_clients:
                                response = json.dumps({"event": "CONNECTION_ERROR", "text": "[CONNECTION FAILED]\nClient name already exists!\nChoose different\n"})
                                conn.sendall(response.encode('utf-8'))
                                break                                 
                            else:   
                                connected_clients.append(data_dict.get("clientName"))
                                connected_clients_conn[data_dict.get("clientName")] = conn
                                broadcast_message = json.dumps({"event": "JOINED", "clientName": f"{data_dict.get('clientName')}","text": f"USER UPDATE: {data_dict.get('clientName')}, JOINED!\n"})
                                for client in list(connected_clients):                 
                                    try:                                              
                                        connected_clients_conn[client].sendall(broadcast_message.encode('utf-8'))
                                    except OSError:                                   
                                        pass                                          

                        elif (data_dict.get("type") == "LEAVE"):
                            broadcast_message = json.dumps({"event": "LEFT", "clientName": f"{data_dict.get('clientName')}","text": f"USER UPDATE: {data_dict.get('clientName')}, LEFT!\n"})
                            for client in list(connected_clients):                 
                                 try:                                              
                                     connected_clients_conn[client].sendall(broadcast_message.encode('utf-8'))
                                 except OSError:                                   
                                     pass                                          

                            if data_dict.get("clientName") in connected_clients:   
                                connected_clients.remove(data_dict.get("clientName"))
                            if data_dict.get("clientName") in connected_clients_conn:
                                 del connected_clients_conn[data_dict.get("clientName")]
                            break

                        else:
                            broadcast_message = json.dumps({"event": "message", "clientName": f"{data_dict.get('clientName')}", "text": f"{data_dict.get('text')}\n"})
                            for client in list(connected_clients):                 
                                if (client == data_dict.get("clientName")):
                                    continue
                                try:                                              
                                    connected_clients_conn[client].sendall(broadcast_message.encode('utf-8'))
                                except OSError:                                  
                                    pass                                          

                    except json.JSONDecodeError:
                        print(f"[ERROR] Invalid JSON recieved from {addr}")
                        error_message = json.dumps({"event": "CONNECTION_ERROR", "text": "[Error] Invalid JSON format\n"})
                        conn.sendall(error_message.encode('utf-8'))
                        break                                              

            finally:
                print(f"[DISCONNECTED] {addr}")
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
                                                                       
                if client_name in connected_clients:
                    connected_clients.remove(client_name)
                if client_name in connected_clients_conn:
                    del connected_clients_conn[client_name]


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Listening] Server is listening on {HOST} : {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()