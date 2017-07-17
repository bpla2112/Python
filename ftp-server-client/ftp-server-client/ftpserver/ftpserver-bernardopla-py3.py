#!/usr/bin/python3
# FTP Server
# Bernardo Pla - 3885008
# CNT 4713 - Project 1

# Necessary imports
import os
import os.path
import sys
from socket import *
import argparse
import threading
import configparser
import uuid
from userdict import *
from userclass import *

#global variables
tList = []
config = configparser.RawConfigParser()
cfgPath = os.path.abspath('serverconfig.txt')
config.read(cfgPath)

#Read and assign values from serverconfig
FTP_ROOT = config['serverconfig']['FTP_ROOT']
FTP_MODE = config['serverconfig']['FTP_MODE']
DATA_PORT_RANGE_MAX = config.getint('serverconfig', 'DATA_PORT_RANGE_MAX')
DATA_PORT_RANGE_MIN = config.getint('serverconfig', 'DATA_PORT_RANGE_MIN')
DATA_PORT_FTP_SERVER = config.getint('serverconfig', 'DATA_PORT_FTP_SERVER')
FTP_ENABLED = config.getint('serverconfig', 'FTP_ENABLED')
MAX_USER_SUPPORT = config.getint('serverconfig', 'MAX_USER_SUPPORT')
WELCOME_MSG = config['serverconfig']['WELCOME_MSG']
FTP_LOG = config['serverconfig']['FTP_LOG']
FTP_SERVICE_PORT = config['serverconfig']['FTP_SERVICE_PORT']

uconfig = configparser.RawConfigParser()
uconfigpath = os.path.abspath('conf/users.cfg')
uconfig.read(uconfigpath)

TESTUSER = uconfig['user1']['username']
TESTPASS = uconfig['user1']['password']
TESTROLE = uconfig['user1']['role']

#parsing server arguments
argParser = argparse.ArgumentParser(prog="python3 ftpserver-bernardopla-py3", description="parsing server commands")
argParser.add_argument("-p", "--port", default=DATA_PORT_FTP_SERVER, help="FTP Server Port")
argParser.add_argument("-c", "--config", default="serverconfig.txt", help="config file")
argParser.add_argument("-m", "--maxconnections", default=200, help="maximum server load")
argParser.add_argument("-uf", "--userdb", help="user file path")
args = argParser.parse_args()

currwd = os.path.abspath('.')
mode = 'I' # declare default binary mode
hostname = "cnt4713.cs.fiu.edu"
allmyusers = userdict()
curruser = ''
currpass =''
userpath = os.path.join(currwd, FTP_ROOT)
print(userpath)


def handleClient(connectionSocket, addr):
    try:
        print("Client connecting now...")
        print(addr)
        lthread = threading.local()
        msg = "Welcome to the club\n"
        connectionSocket.send(msg.encode())
        
        while True:
            print("Current ThreadId: ", threading.current_thread())
            clientmsg = connectionSocket.recv(1024).decode() #this is cmd
            print(clientmsg)
            clientmsg = clientmsg.upper()
            print(str(connectionSocket))
            if(clientmsg[0:3] == "GET" or clientmsg[0:4] == "RETR"):
                ftp_get(connectionSocket, clientmsg, lthread)
            
            if(clientmsg[0:3] == "PWD"):
                ftp_pwd(connectionSocket, clientmsg, lthread)

            if(clientmsg[0:4] == "TYPE"):
                ftp_type(connectionSocket, clientmsg)
            
            if(clientmsg[0:3] == "CWD"):
                ftp_cwd(connectionSocket, clientmsg)
            
            if(clientmsg[0:4] == "USER"):
                ftp_user(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:3] == "PASS"):
                ftp_pass(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "CDUP"):
                ftp_cdup(connectionSocket, clientmsg)

            if(clientmsg[0:4] == "LIST" or clientmsg[0:2] == "LS"):
                ftp_list(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "PORT"):
                ftp_port(connectionSocket, clientmsg, lthread)

            if(clientmsg[0:4] == "NOOP"):
                ftp_noop(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "DELE" or clientmsg[0:6] == "DELETE"):
                ftp_dele(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:3] == "RMD" or clientmsg[0:5] == "RMDIR"):
                ftp_rmd(connectionSocket, lthread, clientmsg)

            if (clientmsg[0:3] == "MKD" or clientmsg[0:5] == "MKDIR"):
                ftp_mkd(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "NOOP"):
                ftp_noop(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:3] == "PUT" or clientmsg[0:4] == "STOR"):
                ftp_stor(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "APPE" or clientmsg[0:6] == "APPEND"):
                ftp_appe(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "STOU" or clientmsg[0:7] == "SUNIQUE"):
                ftp_stou(connectionSocket, lthread, clientmsg)

            if(clientmsg[0:4] == "CDUP" or clientmsg[0:5] == "CD .."):
                ftp_cdup(connectionSocket, clientmsg, lthread)

            if(clientmsg[0:4] == "QUIT"):
                ftp_quit(connectionSocket, lthread, clientmsg)


    except OSError as e:
        print("Oh no. Socket Error: ", e)
        lthread.response = 'Command Error: Please Try again! \r\n'
        connectionSocket.send(lthread.response.encode())

def endoftheWorld():
    global tList
    for t in tList:
        t.join()

#FTP functions
def ftp_get(connectionSocket, clientmsg, lthread):
    print("get was called")
    clientfile = clientmsg[5:-2].lower()
    print(clientfile)
    filename = os.path.join(currwd, clientfile)
    if (os.path.isfile(filename)):
        print("Downloading: ", filename)
        if(mode == "I"): #binary mode
            file = open(filename, 'rb')
        else:
            #ascii mode
            file = open(filename, 'r')
        lthread.response = '150'
        connectionSocket.send(lthread.response.encode())
        filedata = file.read(1024)
        datasocket(lthread)
        while filedata:
            connectionSocket.send(filedata)
            filedata = file.read(1024)
        file.close()
        lthread.response = '226 transfer ' + filename + ' has been completed'
    else:
        lthread.response = 'ERROR: File does not exits \r\n'
        connectionSocket.send(lthread.response.encode())

def ftp_pwd(connectionSocket, clientmsg, lthread):
    print("PWD/LIST called")
    msg = os.getcwd()
    if(msg == '.'):
        msg = '/'
        lthread.response = '226' + msg
    else:
        msg = '/' + msg
        lthread.response = '226' + msg
    connectionSocket.send(lthread.response.encode())

def ftp_type(connectionSocket, clientmsg): # not sure
    global mode
    print("TYPE was called")
    if(clientmsg[5] == 'I'):
        mode = clientmsg[5]
        connectionSocket.send('200 Binary type enabled\r\n', mode)
    if(clientmsg[5] == 'A'):
        mode = clientmsg[5]
        connectionSocket.send('200 ASCII type enabled\r\n', mode)


def ftp_user(connectionSocket, lthread, clientmsg):
    print("USER was called")
    global allmyusers
    global curruser
    global currwd
    values = clientmsg.split(' ')
    name = values[1].strip()
    #password = values[2].strip()
    # curruser = allmyusers.matchedUsers(name.lower())
    curruser = name
    if(curruser == TESTUSER.upper() and TESTPASS.upper() in clientmsg):
        lthread.response = '230 Access Granted'
        connectionSocket.send(lthread.response.encode())
    else:
        lthread.response = '500 Access Denied'
        connectionSocket.send(lthread.response.encode())
    # = os.path.join(currwd, FTP_ROOT, curruser)
    #currwd = userwd
    print(currwd, curruser)
    lthread.response = 'Your current directory: ' #+ userwd
    connectionSocket.send(lthread.response.encode())


# needs to be changed
def ftp_pass(connectionSocket, lthread, clientmsg):
    print("PASS was called")
    global allmyusers
    global curruser
    values = clientmsg.split(' ')
    password = values[1].strip()
    #print(curruser.getupass())

    if(password  == TESTPASS.upper()):
        lthread.response = "230 Access Granted"
        connectionSocket.send(lthread.response.encode())
    else:
        lthread.response = '500 Incorrect password. Access Denied'
        connectionSocket.send(lthread.response.encode())



def ftp_cwd(connectionSocket, clientmsg):
    print("CWD was called")
    changewd = clientmsg[4:-2]
    if changewd == '/':
        connectionSocket.cwd = FTP_ROOT
    elif changewd[0] == '/':
        connectionSocket.cwd = os.path.join(FTP_ROOT, changewd[1:])
    else:
        connectionSocket.cwd = os.path.join(connectionSocket.cwd, changewd)
    clientmsg.send('250 OK \r\n')

def ftp_cdup(connectionSocket, clientmsg, lthread):
    global currwd

    # currwd = os.path.abspath(os.path.join(currwd, '..'))
    currwd = os.chdir(userpath)
    lthread.response = '200 OK \r\n'
    connectionSocket.send(lthread.response.encode())

def ftp_port(connectionSocket, clientmsg, lthread):
    lthread.response = clientmsg[5:].split(',')
    lthread.dataAddress = '.'.join(lthread.response[:4])
    lthread.dataPort = (int(lthread.response[4]) << 8) + int(lthread.response[5])
    print(str(lthread.dataPort))

    lthread.msg = '200 Port Obtained \r\n'
    connectionSocket.send(lthread.msg.encode())

def datasocket(lthread):
    datasock = socket(AF_INET, SOCK_STREAM)
    datasock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    datasock.connect((lthread.dataAddress, lthread.dataPort))

def stopdatasocket(lthread):
    global datasock
    lthread.dataSocket = datasocket(lthread)
    datasock.close()

def ftp_list(connectionSocket, lthread, clientmsg):
    global currwd
    print("LIST was called")
    lthread.response = "150 Opening data connection for file list"
    connectionSocket.send(lthread.response.encode())
    print(currwd)
    datasocket(lthread)

    for file in os.listdir(currwd):
        l = os.path.join(currwd, file)
        lthread.list = l + '\r\n'
        connectionSocket.send(lthread.list.encode())
    lthread.response = '226 Listing completed\r\n'
    connectionSocket.send(lthread.response.encode())

def ftp_noop(connectionSocket, lthread, clientmsg):
    print("NOOP was called")
    lthread.response = '200 OK \r\n'
    connectionSocket.send(lthread.response.encode())

def ftp_stor(connectionSocket, lthread, clientmsg):
    filename = os.path.join(currwd, clientmsg[5:-2])
    print("uploading ", filename)
    if (os.path.getsize(filename) == 0):
        lthread.response = '500 File Denied'
        connectionSocket.send(lthread.response.encode())
    elif(mode == "I"):
        file = open(filename, 'wb')
    else:
        file = open(filename, 'w')
    lthread.response = '150'
    connectionSocket.send(lthread.response.encode())
    datasocket(lthread)
    while True:
        filedata = connectionSocket.recv(1024)
        if not filedata:
            break
        file.write(filedata)
    file.close()
    lthread.response = '226 Stor function completed'
    connectionSocket.send(lthread.response.encode())

def ftp_stou(connectionSocket, lthread, clientmsg):
    filename = os.path.join(currwd, clientmsg[5:-2])
    print("uploading ", filename)
    fileprefix = uuid.uuid4()
    if (mode == "I"):
        file = open(filename, 'wb')
    else:
        file = open(filename, 'w')
    lthread.response = '150'
    connectionSocket.send(lthread.response.encode())
    datasocket(lthread)
    while True:
        filedata = connectionSocket.recv(1024)
        if not filedata:
            break
        file.write(filedata)
    file.close()
    newfilename = fileprefix + '_' + filename
    os.rename(filename, newfilename)
    lthread.response = '226 Stor function completed'
    connectionSocket.send(lthread.response.encode())


def ftp_appe(connectionSocket, lthread, clientmsg):
    filename = os.path.join(currwd, clientmsg[5:-2])
    print("uploading ", filename)
    if (mode == "A"):
        file = open(filename, 'w')
    lthread.response = '150'
    connectionSocket.send(lthread.response.encode())
    datasocket(lthread)
    while True:
        filedata = connectionSocket.recv(1024)
        if not filedata:
            break
        file.write(filedata)
    file.close()
    lthread.response = '226 Stor function completed'
    connectionSocket.send(lthread.response.encode())

def ftp_mkd(connectionSocket, lthread, clientmsg):
    try:

        directoryname = os.path.join(currwd, clientmsg[4:-1])
        os.mkdir(directoryname)
        lthread.response = '257 Directory ' + directoryname +' was created'
        connectionSocket.send(lthread.response.encode())
    except OSError:
        lthread.response = 'Creation failure \r\n'
        connectionSocket.send(lthread.response.encode())

def ftp_dele(connectionSocket, lthread, clientmsg): #for files
    filename = os.path.join(currwd, clientmsg[5:-1].lower())
    if(os.path.isfile(filename)):
        os.remove(filename)
        lthread.response = '250 File was deleted \r\n'
        connectionSocket.send(lthread.response.encode())
    else:
        lthread.response = 'FILE NOT FOUND \r\n'
        connectionSocket.send(lthread.response.encode())

def ftp_rmd(connectionSocket, lthread, clientmsg): #for directories
    directoryname = os.path.join(currwd, clientmsg[4:-1])
    if(directoryname != FTP_ROOT):
        os.remove(directoryname)
    else:
        lthread.response = '450 Directory cannot be deleted. This is a root directory\r\n'
        connectionSocket.send(lthread.response.encode())
    lthread.response = '250 Directory was deleted \r\n'
    connectionSocket.send(lthread.response.encode())

def ftp_rnfr(connectionSocket, lthread, clientmsg):
    lthread.toberenamed = os.path.join(currwd, clientmsg[5:-1])
    lthread.response = '350 Ready to rename file \r\n'
    connectionSocket.send(lthread.response.encode())

def ftp_fnto(connectionSocket, lthread, clientmsg):
    newfilename = os.path.join(currwd, clientmsg[5:-1])
    os.rename(lthread.toberenamed, newfilename)
    lthread.response = '250 File successfully renamed'
    connectionSocket.send(lthread.response.encode())

def retrusers():
    global allmyusers

    with open('conf/users.cfg') as users:
        for line in users:
            if line[0] != '#':
                attributes = line.split(' ')
                allmyusers.newUser(userclass(attributes[0], attributes[1], attributes[2]))
                print(str(allmyusers))

def ftp_quit(connectionSocket, lthread, clientmsg):
    lthread.response = "221 Goodbye Thanks for using FTP"
    connectionSocket.send(lthread.response.encode())
    connectionSocket.close()

#main function here
def main():
    try:
        global tList
        #retrusers()
        
        serverPort = DATA_PORT_FTP_SERVER
        serverSocket = socket(AF_INET, SOCK_STREAM)
        serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        serverSocket.bind((hostname, serverPort))
        serverSocket.listen(15)
        print("The server is ready to receive\n")
        # print(str(WELCOME_MSG))


        while True:
            connectionSocket, addr = serverSocket.accept()
            print("Connection has entered, ", connectionSocket, " ", addr)
            t = threading.Thread(target=handleClient, args=(connectionSocket, addr))
            t.start()
            tList.append(t)
            print("Job running\n")
            print("Waiting for another connection\n")

    except KeyboardInterrupt:
        print("KeyboardInterrupt Detected. Closing connection")
        endoftheWorld()
        serverSocket.close()
    
    print("DONE!")
    sys.exit(0)


if __name__ == "__main__":
    main()