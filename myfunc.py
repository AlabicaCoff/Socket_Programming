import socket
import os
from getpass import getpass

def randomPort():
    s = socket.socket()
    s.bind(('', 0))
    return s.getsockname()[1]

def resetLogin():
    global username, password
    username = ""
    password = ""


def isSocketConnected(client):
    if client is None or client._closed:
        return False
    else:
        return True


def sendRequest(client, msg):
    client.send(msg.encode())


def recvResponse(client, rcvBuf, showResponse = True):
    response = client.recv(rcvBuf)
    if showResponse:
        print(response.decode().strip())
    return response


def user(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    global username, password
    if options > 4:
        print("Usage: user username [password] [account]")
        return
    elif options == 4 or options == 3:
        username, password = args[1], args[2]
        sendRequest(client, f"USER {username}\r\n")
        response = recvResponse(client, rcvBuf)
    elif options == 1:
        username = input(f"Username ").strip()
        sendRequest(client, f"USER {username}\r\n")
        response = recvResponse(client, rcvBuf, False)

        if "501" in response.decode():
            print("Usage: user username [password] [account]")
            return
        
        password = getpass("Password: ").strip()
        print()
    else:
        username = args[1]
        sendRequest(client, f"USER {username}\r\n")
        response = recvResponse(client, rcvBuf)
        password = getpass("Password: ").strip()
        print()

    sendRequest(client, f"PASS {password}\r\n")
    response = recvResponse(client, rcvBuf)
    
    if "230" in response.decode():
        return
    
    print("Login failed.")
    

def userLoginViaOpen(client, host, rcvBuf):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    global username, password
    username = input(f"User ({host}:(none)): ").strip()
    sendRequest(client, f"USER {username}\r\n")
    response = recvResponse(client, rcvBuf)

    if "331" in response.decode():
        password = getpass("Password: ").strip()
        print()
        sendRequest(client, f"PASS {password}\r\n")
        response = recvResponse(client, rcvBuf)
        
        if "230" in response.decode():
            return
    print("Login failed.")


def connectSuccess(client, host, rcvBuf):
    print(f"Connected to {host}")
    recvResponse(client, rcvBuf)

    sendRequest(client, "OPTS UTF8 ON\r\n")
    recvResponse(client, rcvBuf)

    userLoginViaOpen(client, host, rcvBuf)


def connectSocket(host, port, rcvBuf):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((host, int(port)))
        connectSuccess(client, host, rcvBuf)
        return client
    except TimeoutError:
        print("> ftp: connect :Connection timed out")
    except socket.gaierror:
        print("Unknown host " + host)
    return None


def opens(client, args, options, rcvBuf = 1024):
    if isSocketConnected(client):
        host = client.getpeername()[0]
        print(f"Already connected to {host}, use disconnect first.")
        return client
    
    port = 21
    if options == 1:
        host = input("To ").strip()
    elif options == 3:
        host = args[1]
        port = int(args[2])
    else:
        host = args[1]

    if options > 3 or host == "":
        print("Usage: open host name [port]")
        return
    
    return connectSocket(host, port, rcvBuf)


def close(client, checkIsConnected = True, rcvBuf = 2048):
    global username, password
    if checkIsConnected and not isSocketConnected(client):
        print("Not connected.")
        return

    if client:
        sendRequest(client, "QUIT\r\n")
        recvResponse(client, rcvBuf)
        client.close()
        resetLogin()


def checkUserLogin():
    global username, password
    return (username == "" and password == "")


def pwd(client, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    sendRequest(client, f"XPWD\r\n")
    recvResponse(client, rcvBuf)


def cd(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    if options >= 2:
        target = args[1]
    elif options == 1:
        target = input("Remote directory ")

    sendRequest(client, f"CWD {target}\r\n")
    recvResponse(client, rcvBuf)
    

def checkInputEmpty(input):
    return (input is None or input == "")
    

def rename(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    if options >= 3:
        fromName, toName = args[1], args[2]
    elif options == 1:
        fromName = input("From name ")
        if checkInputEmpty(fromName):
            print("rename from-name to-name.")
            return
        
        toName = input("To name ")
        if checkInputEmpty(toName):
            print("rename from-name to-name.")
            return
    else:
        toName = input("To name ")
        if checkInputEmpty(toName):
            print("rename from-name to-name.")
            return
        
    sendRequest(client, f"RNFR {fromName}\r\n")
    response = recvResponse(client, rcvBuf)

    if "350" in response.decode():
        sendRequest(client, f"RNTO {toName}\r\n")
        response = recvResponse(client, rcvBuf)
    

def ascii(client, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    sendRequest(client, f"TYPE A\r\n")
    recvResponse(client, rcvBuf)


def binary(client, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    sendRequest(client, f"TYPE I\r\n")
    recvResponse(client, rcvBuf)


def delete(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    if options == 1:
        targetFile = input("Remote file ")
    if options == 2:
        targetFile = args[1]

    sendRequest(client, f"DELE {targetFile}\r\n")
    recvResponse(client, rcvBuf)


def ls(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    remoteDir = ""
    localFile = None
    if options > 3:
        print("Usage: ls remote directory local file.")
        return
    elif options == 2:
        remoteDir = args[1]
    elif options == 3:
        remoteDir = args[1]
        localFile = args[2]

    addr = client.getsockname()[0]
    if addr == "127.0.0.1":
        port = 12000
    else:
        port = randomPort()

    last1, last2 = port // 256, port % 256
    portArg = ",".join(addr.split(".")) + f",{last1},{last2}"

    sendRequest(client, f"PORT {portArg}\r\n")
    recvResponse(client, rcvBuf)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((addr, port))
    data_socket.listen(8)

    sendRequest(client, f"NLST {remoteDir}\r\n")
    response = recvResponse(client, rcvBuf)

    if "550" in response.decode():
        return

    data_connection, _ = data_socket.accept()
    result = b""
    result = data_connection.recv(2048)
    result = result.decode()
    data_connection.close()
    data_socket.close()

    if options == 3:
        with open(localFile, 'w', newline="") as file:
            file.write(result)
    else:
        print(result, end="")

    recvResponse(client, rcvBuf)
    print("ftp: 13 bytes sent in 0.00Seconds 13000.00Kbytes/sec.")

    
def get(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    remoteFile = ""
    localFile = None
    if options == 1:
        remoteFile = input("Remote file ")

        if remoteFile == "":
            print("Remote file get [ local-file ].")
            return
        
        localFile = input("Local file ")

        if localFile == "":
            localFile = remoteFile
    elif options == 2:
        remoteFile = args[1]
        localFile = args[1]
    elif options >= 3:
        remoteFile = args[1]
        localFile = args[2]

    addr = client.getsockname()[0]
    if addr == "127.0.0.1":
        port = 12000
    else:
        port = randomPort()

    last1, last2 = port // 256, port % 256
    portArg = ",".join(addr.split(".")) + f",{last1},{last2}"

    sendRequest(client, f"PORT {portArg}\r\n")
    recvResponse(client, rcvBuf)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((addr, port))
    data_socket.listen(8)

    sendRequest(client, f"RETR {remoteFile}\r\n")
    response = recvResponse(client, rcvBuf)

    if "550" in response.decode() or "530" in response.decode():
        return
    
    data_connection, _ = data_socket.accept()
    data = data_connection.recv(2048)
    data_connection.close()
    data_socket.close()

    recvResponse(client, rcvBuf)
    print("ftp: 13 bytes sent in 0.00Seconds 13000.00Kbytes/sec.")

    with open(localFile, 'wb', newline="") as file:
        file.write(data)
        file.close()


def put(client, args, options, rcvBuf = 1024):
    if not isSocketConnected(client):
        print("Not connected.")
        return
    
    localFile = ""
    remoteFile = ""
    if options == 1:
        localFile = input("Local file ")

        if localFile == "":
            print("Remote file get [ local-file ].")
            return
        
        remoteFile = input("Remote file ")

        if remoteFile == "":
            remoteFile = localFile
    elif options == 2:
        localFile = args[1]
        remoteFile = args[1]
    elif options >= 3:
        localFile = args[1]
        remoteFile = args[2]

    if not os.path.exists(localFile):
        print(f"{localFile}: File not found")
        return
    
    addr = client.getsockname()[0]
    if addr == "127.0.0.1":
        port = 12000
    else:
        port = randomPort()

    last1, last2 = port // 256, port % 256
    portArg = ",".join(addr.split(".")) + f",{last1},{last2}"

    sendRequest(client, f"PORT {portArg}\r\n")
    recvResponse(client, rcvBuf)

    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.bind((addr, port))
    data_socket.listen(8)

    sendRequest(client, f"STOR {remoteFile}\r\n")
    recvResponse(client, rcvBuf)

    data_conn, _ = data_socket.accept()
    with open(localFile, "rb") as file:
        data = file.read(2048)
        file.close()
    data_conn.send(data)
    data_conn.close()
    data_socket.close()

    recvResponse(client, rcvBuf)
    print("ftp: 13 bytes sent in 0.00Seconds 13000.00Kbytes/sec.")
