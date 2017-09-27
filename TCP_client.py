import socket

target_host = "0.0.0.0"
target_port = 9999

# create a socket
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# connect to the client
client.connect((target_host,target_port))

#send messages
client.send("ABCDEEEEFFFF")

#receive messages
response = client.recv(4096)

print response
