# FTP Client
# Contributed by L.A.A.M.
# ********************************************************************************
# **                   **
# ** References                                                                 **
# ** http://www.slacksite.com/other/ftp.html#active                             **
# ** https://www.ietf.org/rfc/rfc959.txt                                        **
# ** Computer-Networking Top-Down Approach 6th Edition by Kurose and Ross       **
# ** computer ftp client                                                        **
# **                                                                            **
# ** Tested with inet.cis.fiu.edu  -- FIXED Port 21                             **
# ** Commands are not case sensitive                                            **
# **                                                                            **
# ** Built for Python 2.7.x. FTP Client Active Mode Only                        **
# ** Usage: Python ftp.py hostname [username] [password]                        **
# ** username and password are optional when invoking ftp.py                    **
# ** if not supplied, use command LOGIN                                         **
# ** Inside of ftp client, you can type HELP for more information               **
# ********************************************************************************

#### This new version was modified by Francisco R. Ortega to work with Python 3
#### Beta version

#import necessary packages.
import os
import os.path
import errno
import traceback
import sys
from socket import *
import configparser
import argparse
from userdict import *
from userclass import *

configParser = configparser.RawConfigParser()
configPath = os.path.abspath('clientconfig.txt')
configParser.read(configPath)
allmyusers = userdict()
curruser = ''
currpass = ''

#Global constants
USAGE = "usage: Python ftp hostname [username] [password]"

RECV_BUFFER = 1024
FTP_PORT = 21
CMD_QUIT = "QUIT"
CMD_HELP = "HELP"
CMD_LOGIN = "LOGIN"
CMD_LOGOUT = "LOGOUT"
CMD_LS = "LS"
CMD_PWD = "PWD"
CMD_PORT = "PORT"
CMD_DELETE = "DELETE"
CMD_PUT = "PUT"
CMD_GET = "GET"

#the ports ranges from MIN to MAX and values from config file 
DATA_PORT_MAX = configParser.getint('clientconfig', 'DATA_PORT_MAX')
DATA_PORT_MIN = configParser.getint('clientconfig', 'DATA_PORT_MIN')
FTP_PORT = configParser.getint('clientconfig', 'DEFAULT_FTP_PORT')
DEFAULT_MODE = configParser['clientconfig']['DEFAULT_MODE']
DEFAULT_DEBUG_MODE = configParser['clientconfig']['DEFAULT_DEBUG_MODE']
DEFAULT_VERBOSE_MODE = configParser['clientconfig']['DEFAULT_VERBOSE_MODE']
DEFAULT_TEST_FILE = configParser['clientconfig']['DEFAULT_TEST_FILE']
DEFAULT_LOG_FILE = configParser['clientconfig']['DEFAULT_LOG_FILE']
FTP_SERVICE_PORT = configParser.getint('clientconfig', 'FTP_SERVICE_PORT')

#data back log for listening.
DATA_PORT_BACKLOG = 1

#argparse section
argParser = argparse.ArgumentParser(description="Parsing command line arguments.", prog="python3 ftpclient3v2")
argParser.add_argument("-hn", help="hostname")
argParser.add_argument("-u", "--username", help="username")
argParser.add_argument("-w", default="", help="password")
argParser.add_argument("-fp", default=FTP_PORT, help="FTP Server Port")
argParser.add_argument("-P", "--passive", help="passive mode")
argParser.add_argument("-A", "--active", help="active mode")
argParser.add_argument("-D", "--debug", help="debug mode toggle")
argParser.add_argument("-V", "--verbose", help="verbose mode")
argParser.add_argument("-dpr", help="data ports")
argParser.add_argument("-c", "--config", default="clientconfig.txt", help="config file")
argParser.add_argument("-t", help="test file")
argParser.add_argument("-T", help="default test file")
argParser.add_argument("-L", "--log", default="./ftpserver/log/clientlog.txt", help="log file")
argParser.add_argument("-ALL", default="allFalse", help="log all file output")
argParser.add_argument("-ONLY", default="allFalse", help="log output to log file")
argParser.add_argument("-v", "--version", help="gets version info")
argParser.add_argument("-info", help="prints information on user and ftp client")
args = argParser.parse_args()


#global variables
#store the next_data_port use in a formula to obtain
#a port between DATA_POR_MIN and DATA_PORT_MAX
next_data_port = 1
hostname = "cnt4713.cs.fiu.edu"
username = ""
password = ""

#entry point main()
def main():
    global hostname
    global username
    global password

    #retrusers()

    logged_on = False
    logon_ready = False
    print("FTP Client v1.0")
    if (len(sys.argv) < 2):
         print(USAGE)
    if (len(sys.argv) == 2):
        hostname = sys.argv[1]
    if (len(sys.argv) == 4):
        username = sys.argv[2]
        password = sys.argv[3]
        logon_ready = True


    print("********************************************************************")
    print("**                        ACTIVE MODE ONLY                        **")
    print("********************************************************************")
    print(("You will be connected to host: " + hostname))
    print("Type HELP for more information")
    print("Commands are NOT case sensitive\n")


    ftp_socket = ftp_connecthost(hostname)
    ftp_recv = ftp_socket.recv(RECV_BUFFER)
    ftp_code = ftp_recv[:3]
    #
    #note that in the program there are many .strip('\n')
    #this is to avoid an extra line from the message
    #received from the ftp server.
    #an alternative is to use sys.stdout.write
    print(msg_str_decode(ftp_recv,True))
    #
    #this is the only time that login is called
    #without relogin
    #otherwise, relogin must be called, which included prompts
    #for username
    #
    if (logon_ready):
        logged_on = login(ftp_socket, 2)

    keep_running = True

    while keep_running:
        try:
            rinput = input("FTP>")
            if (rinput is None or rinput.strip() == ''):
                continue
            tokens = rinput.split()
            cmdmsg , logged_on, ftp_socket = run_cmds(tokens,logged_on,ftp_socket)
            if (cmdmsg != ""):
                print(cmdmsg)
        except OSError as e:
        # A socket error
          print("Socket error:",e)
          strError = str(e)
          #this exits but it is better to recover
          if (strError.find("[Errno 32]") >= 0): 
              sys.exit()

    #print ftp_recv
    try:
        ftp_socket.close()
        print("Thank you for using FTP 1.0")
    except OSError as e:
        print("Socket error:",e)
    sys.exit()

def run_cmds(tokens,logged_on,ftp_socket):
    global username
    global password
    global hostname
    cmd = tokens[0].upper()
   
    if (cmd == CMD_QUIT):
        quit_ftp(logged_on,ftp_socket)
        return "",logged_on, ftp_socket
    
    if (cmd == CMD_HELP or cmd == "?"):
        help_ftp()
        return "",logged_on, ftp_socket

    if (cmd == CMD_PWD):
        pwd_ftp(ftp_socket)
        return "",logged_on, ftp_socket

    if(cmd == "MKD"):
        mkd_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if(cmd == "CWD"):
        cwd_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if(cmd == "LPWD"):
        lpwd_ftp()
        return "", logged_on, ftp_socket

    if(cmd == "CDUP"):
        cdup_ftp(ftp_socket)
        return "", logged_on, ftp_socket

    if (cmd == CMD_LS or cmd == "LIST"):
        #FTP must create a channel to received data before
        #executing ls.
        #also makes sure that data_socket is valid
        #in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            ls_ftp(tokens,ftp_socket,data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[LS] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_LOGIN):
        global username
        global password
        username, password, logged_on, ftp_socket \
        = relogin(logged_on, tokens, hostname, ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_LOGOUT):
        logged_on,ftp_socket = logout(logged_on,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_DELETE):
        delete_ftp(tokens,ftp_socket)
        return "",logged_on, ftp_socket

    if (cmd == CMD_PUT or cmd == "APPE" or cmd == "APPEND"):
        # FTP must create a channel to received data before
        # executing put.
        #  also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            put_ftp(tokens,ftp_socket,data_socket),logged_on, ftp_socket
            return ""
        else:
            return "[PUT] Failed to get data port. Try again.",logged_on, ftp_socket

    if (cmd == CMD_GET):
        # FTP must create a channel to received data before
        # executing get.
        # also makes sure that data_socket is valid
        # in other words, not None
        data_socket = ftp_new_dataport(ftp_socket)
        if (data_socket is not None):
            get_ftp(tokens, ftp_socket, data_socket)
            return "",logged_on, ftp_socket
        else:
            return "[GET] Failed to get data port. Try again.",logged_on, ftp_socket

    return "Unknown command", logged_on, ftp_socket

def str_msg_encode(strValue):
    msg = strValue.encode()
    return msg

def msg_str_decode(msg,pStrip=False):
    #print("msg_str_decode:" + str(msg))
    strValue = msg.decode()
    if (pStrip):
        strValue.strip('\n')
    return strValue

def ftp_connecthost(hostname):

    ftp_socket = socket(AF_INET, SOCK_STREAM)
    #to reuse socket faster. It has very little consequence for ftp client.
    ftp_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    ftp_socket.connect((hostname, FTP_PORT))
    print (ftp_socket)
    return ftp_socket

def ftp_new_dataport(ftp_socket):
    global next_data_port
    dport = next_data_port
    host = gethostname()
    host_address = gethostbyname(host)
    next_data_port = next_data_port + 1 #for next next
    dport = (int(DATA_PORT_MIN) + dport) % int(DATA_PORT_MAX)

    print(("Preparing Data Port: " + host + " " + host_address + " " + str(dport)))
    data_socket = socket(AF_INET, SOCK_STREAM)
    # reuse port
    data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    data_socket.bind((host_address, dport))
    data_socket.listen(DATA_PORT_BACKLOG)

    #the port requires the following
    #PORT IP PORT
    #however, it must be transmitted like this.
    #PORT 192,168,1,2,17,24
    #where the first four octet are the ip and the last two form a port number.
    host_address_split = host_address.split('.')
    high_dport = str(dport // 256) #get high part
    low_dport = str(dport % 256) #similar to dport << 8 (left shift)
    print(high_dport)
    print(low_dport)
    port_argument_list = host_address_split + [high_dport,low_dport]
    port_arguments = ','.join(port_argument_list)
    cmd_port_send = CMD_PORT + ' ' + port_arguments + '\r\n'
    print(cmd_port_send)


    try:
        ftp_socket.send(str_msg_encode(cmd_port_send))
    except socket.timeout:
        print("Socket timeout. Port may have been used recently. wait and try again!")
        return None
    except socket.error:
        print("Socket error. Try again")
        return None
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    return data_socket

def pwd_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("PWD\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def mkd_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("MKD\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg, True))

def rmd_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("RMD\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg, True))


def get_ftp(tokens, ftp_socket, data_socket):
    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    remote_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = remote_filename

    ftp_socket.send(str_msg_encode("RETR " + remote_filename + "\r\n"))

    print(("Attempting to write file. Remote: " + remote_filename + " - Local:" + filename))

    msg = ftp_socket.recv(RECV_BUFFER)
    strValue = msg_str_decode(msg)
    tokens = strValue.split()
    if (tokens[0] != "150"):
        print("Unable to retrieve file. Check that file exists (ls) or that you have permissions")
        return

    print(msg_str_decode(msg,True))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename, "wb")  # read and binary modes

    size_recv = 0
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = data_connection.recv(RECV_BUFFER)

        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            file_bin.write(data)
            size_recv += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


### put_ftp
def put_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = local_filename

    if (os.path.isfile(local_filename) == False):
        print(("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path"))
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

    ftp_socket.send(str_msg_encode("STOR " + filename + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename,"rb") #read and binary modes

    size_sent = 0
    #use write so it doesn't produce a new line (like print)
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = file_bin.read(RECV_BUFFER)
        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            data_connection.send(data)
            size_sent += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))


#
def ls_ftp(tokens,ftp_socket,data_socket):

    if (len(tokens) > 1):
        ftp_socket.send(str_msg_encode("LIST " + tokens[1] + "\r\n"))
    else:
        ftp_socket.send(str_msg_encode("LIST\r\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    data_connection, data_host = data_socket.accept()

    msg = data_connection.recv(RECV_BUFFER)
    while (len(msg) > 0):
        print(msg_str_decode(msg,True))
        msg = data_connection.recv(RECV_BUFFER)

    data_connection.close()
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))
    #data_connection.close()

def delete_ftp(tokens, ftp_socket):

    if (len(tokens) < 2):
        print("You must specify a file to delete")
    else:
        print(("Attempting to delete " + tokens[1]))
        ftp_socket.send(str_msg_encode("DELE " + tokens[1] + "\n"))

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def cwd_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("CWD\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg, True))

def lpwd_ftp():
    currwd = os.path.abspath('.')
    print(currwd)

def lls_ftp():
    currwd = os.path.abspath('.')
    print(currwd)
    for file in os.listdir(currwd):
        l = os.path.join(currwd, file)
        listedfiles = l + '\r\n'
    print(listedfiles)

def cdup_ftp(ftp_socket):
    ftp_socket.send(str_msg_encode("CD ..\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg, True))

def stou_ftp(tokens, ftp_socket, data_socket):
    if (len(tokens) < 2):
        print("put [filename]. Please specify filename")
        return

    local_filename = tokens[1]
    if (len(tokens) == 3):
        filename = tokens[2]
    else:
        filename = local_filename

    if (os.path.isfile(local_filename) == False):
        print(("Filename does not exisit on this client. Filename: " + filename + " -- Check file name and path"))
        return
    filestat = os.stat(local_filename)
    filesize = filestat.st_size

    ftp_socket.send(str_msg_encode("STOU " + filename + "\n"))
    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

    print(("Attempting to send file. Local: " + local_filename + " - Remote:" + filename + " - Size:" + str(filesize)))

    data_connection, data_host = data_socket.accept()
    file_bin = open(filename,"rb") #read and binary modes

    size_sent = 0
    #use write so it doesn't produce a new line (like print)
    sys.stdout.write("|")
    while True:
        sys.stdout.write("*")
        data = file_bin.read(RECV_BUFFER)
        if (not data or data == '' or len(data) <= 0):
            file_bin.close()
            break
        else:
            data_connection.send(data)
            size_sent += len(data)

    sys.stdout.write("|")
    sys.stdout.write("\n")
    data_connection.close()

    msg = ftp_socket.recv(RECV_BUFFER)
    print(msg_str_decode(msg,True))

def logout(lin, ftp_socket):
    if (ftp_socket is None):
        print("Your connection was already terminated.")
        return False, ftp_socket

    if (lin == False):
        print("You are not logged in. Logout command will be send anyways")

    print("Attempting to logged out")
    msg = ""
    try:
        ftp_socket.send(str_msg_encode("QUIT\n"))
        msg = ftp_socket.recv(RECV_BUFFER)
    except socket.error:
        print ("Problems logging out. Try logout again. Do not login if you haven't logged out!")
        return False
    print(msg_str_decode(msg,True))
    ftp_socket = None
    return False, ftp_socket #it should only be true if logged in and not able to logout

def quit_ftp(lin,ftp_socket):
    print ("Quitting...")
    logged_on, ftp_socket = logout(lin,ftp_socket)
    print("Thank you for using FTP")
    try:
        if (ftp_socket is not None):
            ftp_socket.close()
    except socket.error:
        print ("Socket was not able to be close. It may have been closed already")
    sys.exit()


# def relogin(username,password,logged_on,tokens,hostname,ftp_socket):
#     if (len(tokens) < 3):
#         print("LOGIN requires more arguments. LOGIN [username] [password]")
#         print("You will be prompted for username and password now")
#         username = input("User:")
#         password = input("Pass:")
#     else:
#         username = tokens[1]
#         password = tokens[2]
#
#     if (ftp_socket is None):
#         ftp_socket = ftp_connecthost(hostname)
#         ftp_recv = ftp_socket.recv(RECV_BUFFER)
#         print((ftp_recv.strip('\n')))
#
#     logged_on = login(username, password, ftp_socket)
#     return username, password, logged_on, ftp_socket

def relogin(logged_on, tokens, hostname, ftp_socket):
    global curruser
    global allmyusers
    global username
    global password
    if ftp_socket is None:
        ftp_socket = ftp_connecthost(hostname)
        ftp_recv = ftp_socket.recv(RECV_BUFFER)
        print((ftp_recv.strip('\n')))
    if len(tokens) < 3:
        print('LOGIN requires more arguments: LOGIN [username] [password], you will be prompted for more.')
        logged_on = login(ftp_socket, 1)
    else:
        username = tokens[1]
        password = tokens[2]
        logged_on = login(ftp_socket, 2)
    if logged_on:
        curruser = allmyusers.matchedUsers(username)
        print(str(curruser))
        return username, password, logged_on, ftp_socket

def retrusers():
    global allmyusers
    with open('ftpserver/conf/users.cfg') as users:
        for items in users:
            if items[0] != '#':
                attributes = items.split(' ')
                allmyusers.newUser(userclass(attributes[0], attributes[1], attributes[2]))
                print(str(allmyusers))


def help_ftp():
    print("FTP Help")
    print("Commands are not case sensitive")
    print("")
    print((CMD_QUIT + "\t\t Exits ftp and attempts to logout"))
    print((CMD_LOGIN + "\t\t Logins. It expects username and password. LOGIN [username] [password]"))
    print((CMD_LOGOUT + "\t\t Logout from ftp but not client"))
    print((CMD_LS + "\t\t prints out remote directory content"))
    print((CMD_PWD + "\t\t prints current (remote) working directory"))
    print((CMD_GET + "\t\t gets remote file. GET remote_file [name_in_local_system]"))
    print((CMD_PUT + "\t\t sends local file. PUT local_file [name_in_remote_system]"))
    print((CMD_DELETE + "\t\t deletes remote file. DELETE [remote_file]"))
    print((CMD_HELP + "\t\t prints help FTP Client"))


# def login(user, passw, ftp_socket):
#     if (user == None or user.strip() == ""):
#         print("Username is blank. Try again")
#         return False;
#
#
#     print(("Attempting to login user " + user))
#     #send command user
#     ftp_socket.send(str_msg_encode("USER " + user + "\n"))
#     msg = ftp_socket.recv(RECV_BUFFER)
#     print(msg_str_decode(msg,True))
#     ftp_socket.send(str_msg_encode("PASS " + passw + "\n"))
#     msg = ftp_socket.recv(RECV_BUFFER)
#     strValue = msg_str_decode(msg,False)
#     tokens = strValue.split()
#     print(msg_str_decode(msg,True))
#     if (len(tokens) > 0 and tokens[0] != "230"):
#         print("Not able to login. Please check your username or password. Try again!")
#         return False
#     else:
#         return True

def login(ftp_socket, loginmethod):
    global username
    global password
    if loginmethod == 1:  # The username and password do not exist
        # First get the user input
        username = input('Enter the account\'s username: ')
        ftp_socket.send(('USER {0}'.format(username).encode()))
        isUser = ftp_socket.recv(RECV_BUFFER).decode()
        print(isUser[0:3])
        if isUser[0:3] == '230':
            # Since the username is good then get the password next
            password = input('Enter the account\'s password: ')
            ftp_socket.send(('PASS {0}'.format(password).encode()))
            password_results = ftp_socket.recv(RECV_BUFFER).decode()
            print(password_results[0:3])
            if password_results[0:3] == '230':
                return username, password, True
            else:
                print('Access Denied: Incorrect Password')
                return username, password, True
        elif isUser[0:3] != '230':
            print('Access granted ')
            return username, password, True
        else:
            print('User not found. Try again')
            return username, password, True

    elif loginmethod == 2:  # The username and password do exist
        ftp_socket.send('USER {0}'.format(username).encode())
        isUser = ftp_socket.recv(RECV_BUFFER).decode()
        print(isUser[0:3])
        if isUser[0:3] == '230':
            ftp_socket.send(('PASS {0}'.format(password).encode()))
            password_results = ftp_socket.recv(RECV_BUFFER).decode()
            print(password_results[0:3])
            if password_results[0:3] == '230':
                return username, password, True
            else:
                print('Invalid Password')
                return username, password, True
        elif isUser[0:3] != '230':
            print('Access granted')
            return username, password, True

        else:
            print('User does not exist')
            return username, password, True

#Calls main function.
main()
