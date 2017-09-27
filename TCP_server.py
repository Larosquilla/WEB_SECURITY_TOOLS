import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 9999

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind((bind._ip,bind_port))

server.listen(5)

print "[*] Listening on %s %d" % (bind_ip,bind_port)

def handle_client(client_socket):
    # 打印出客户端发过来的内容
    request = client_socket.recv(1024)

    print "[*] Received: %s" % request

    #返还一个ACK数据包

    client_socket.send("ACK!")

    client_socket.close()

while True:

    client,addr = server.accept()

    print "[*] Accepted connection from: %s:%d" % (addr[0],addr[1])

    # 挂起线程
    client_handler = threading.Thread(target=handle_client,args=(client,))
    client_handler.start()
