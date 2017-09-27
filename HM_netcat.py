import sys
import socket
import getopt
import threading
import subprocess

# define some global variables

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
    print "BHP Net Tool"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l listen                - listen on [host]:[port] for imcoming connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --command             - initialize a command shell"
    print "-u --upload=destination  - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples:"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    # ?????
    if not len(sys.argv[1:]):
        usage()
    # read the command line option
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            execute = a
        elif o in ("-c","--commandshell"):
            command = True
        elif o in ("-u","--upload"):
            upload_destination = a
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"

        # Do we need to send data from standard i/o?
        if not listen and len(target) and port > 0:
            # read input from command line
            buffer = sys.stdin.read()
            # send data
            client_sender(buffer)

        # ready to listen and upload files or execute command lines
        if listen:
            server_loop()


main()
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # connet to the target host machine
        client.connect((target,port))

        if len(buffer):
            client.send(buffer)
        while True:

            # wait for the data back
            recv_len = 1
            response = ""
            while recv_len:

                data = client.recv(4096)
                recv_len = len(data)
                response+=data

                if recv_len < 4096: #??????????why4096
                    break
            print response,

            # for more input
            buffer = raw_input("")
            buffer += "\n"

            # send out
            client.send(buffer)

    except:

        print "[*] Exception! Exiting."
        client.close()

    def server_loop():
        global target
        # if target is not defined, listen on all ports
        if not len(target):
            target = "0.0.0.0"

        server = socekt.socket(socket.AF_INET,socket.SOCK_STREAM)
        server.bind((target,port))

        server.listen(5)

        while True:
            client_socket,addr = server.accept()

            # split another thread for a new client
            client_thread = threading.Thread(target=client_handler,args=(client_socket,))
            client_thread.start()


    def run_command(command):
        # enter to start a new line
        command = command.rstrip()
        # run the command and reutrn the output
        try:
            output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
        except:
            output = "Failed to execute command.\r\n"

        return output

    def client_handler(client_socket):
        global upload
        global execute
        global command
        # check the upload files
        if len(upload_destination):
            # read all characters
            file_buffer=""

            while True:
                data = client_socket.recv(1024)

                if not data:
                    break
                else:
                    file_buffer += data
            # now we have received these data and try to output
            try:
                file_descriptor = open(upload_destination,"wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                client_socket.send("Successfully saved file to %s\r\n" % upload_destination)
            except:
                client_socket.send("Failed to save file to%s\r\n" % upload_destination)
        if  len(execute):

            output = run_command(execute)

            client_socket.send(output)

        # if a command shell is needed, then we start another loop

        if command:

            while True:
                # alert a window
                client_socket.send("<BHP:#> ")

                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += client_socket.recv(1024) # why 1024?
                    response = run_command(cmd_buffer)

                    client_socket.send(response)
