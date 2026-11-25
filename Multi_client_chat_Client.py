import socket
import sys
import json
import threading
import time

stop_receiver = threading.Event()

SERVER_IP = sys.argv[2]
SERVER_PORT = 9999

# headers
type = "JOIN"
clientName = sys.argv[1]

message = ""

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(10.0)

client.connect((SERVER_IP, SERVER_PORT))

req_message = json.dumps({"type": f"{type}", "clientName": f"{clientName}"})
client.sendall(req_message.encode('utf-8'))

response = client.recv(1024).decode('utf-8')
data_dict = json.loads(response)

if (data_dict.get("event") == "JOINED") and (data_dict.get("clientName") == f"{clientName}"):
    type = "PRESENCE"
    print(f"{data_dict.get('text')}")
else:
    print(f"JOIN failed: {data_dict.get('text')}")
    client.close()
    sys.exit(1)

def receiver():                                          
    while not stop_receiver.is_set():                                         
        try:                                             
            data = client.recv(1024)                     
            if not data:                                 
                break                                    
            msg = json.loads(data.decode('utf-8'))       
            decoded_response = msg.get("text")                   

            if msg.get("event") in ("JOINED", "LEFT"):
                print(f"\n{decoded_response}")
            else:
                print(f"\n{msg.get('clientName')}: {decoded_response}")  
        except (OSError, json.JSONDecodeError):          
            break
                                                      


if type == "PRESENCE":
    client.settimeout(None)  # don't time out while chatting
    threading.Thread(target=receiver, daemon=True).start()   
    while message.lower() != "exit":
        message = input(f"{clientName} | YOU: ")
        if message.lower() == "exit":
            print("\n")
            break
        else:
            print("\n")
            embedded_message = json.dumps({"type": f"{type}", "clientName": f"{clientName}", "text": f"{message}"})
            client.sendall(embedded_message.encode('utf-8'))

if message.lower() == "exit":
    stop_receiver.set()
    type = "LEAVE"
    final_message = json.dumps({"type": f"{type}", "clientName": f"{clientName}"})
    client.sendall(final_message.encode('utf-8'))
    client.shutdown(socket.SHUT_WR)
    time.sleep(0.2)

    client.close()