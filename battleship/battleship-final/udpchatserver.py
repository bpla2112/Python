import socket
import threading
#from battleshipGameREDONEREDONE import BattleshipGameRedoneRedone

serverSocket = ''
CONNECTION_LIST=[]

def accept_client():
    while True:
        #accept    
        clientSocket, cli_add = serverSocket.accept()
        uname = clientSocket.recv(1024)
        CONNECTION_LIST.append((uname, clientSocket))
        print('%s is now connected' %uname)
        thread_client = threading.Thread(target = broadcast_usr, args=[uname, clientSocket])
        thread_client.start()

def broadcast_usr(uname, clientSocket):
    while True:
        try:
            data = clientSocket.recv(1024)
            if data:
                print ("{0} spoke".format(uname))
                b_usr(clientSocket, uname, data)
        except Exception as x:
            print(x)
            break

def b_usr(cs_sock, sender, msg):
    for client in CONNECTION_LIST:
        if client[1] != cs_sock:
            client[1].send(sender)
            client[1].send(msg)


def main():
    global serverSocket
    global CONNECTION_LIST 

    # socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind
    HOST = 'localhost'
    PORT = 5023
    serverSocket.bind((HOST, PORT))

    # listen    
    serverSocket.listen(1)
    print('Chat server started on port : ' + str(PORT))

    thread_ac = threading.Thread(target = accept_client)
    thread_ac.start()

if __name__ == '__main__':
    main()