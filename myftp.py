from myfunc import *

username, password = "", ""
clientSocket = None
commands = ["ascii", "binary", "bye", "cd", "close", "delete", "disconnect", 
            "get", "ls", "open", "put", "pwd", "quit", "rename", "user"]

while True:
    line = input("ftp> ").strip()
    args = line.split()

    command = args[0] if args else None
    # invalid command
    if command not in commands:
        print("Invalid command.")
    # binary
    elif command == commands[0]:
        binary(clientSocket)
    # ascii
    elif command == commands[1]:
        ascii(clientSocket)
    # bye & quit
    elif command == commands[2] or command == commands[12]:
        close(clientSocket, False)
        print()
        break
    # cd
    elif command == commands[3]:
        cd(clientSocket, args, len(args))
    # close & disconnect
    elif command == commands[4] or command == commands[6]:
        close(clientSocket)
    # delete
    elif command == commands[5]:
        delete(clientSocket, args, len(args))
    # get
    elif command == commands[7]:
        get(clientSocket, args, len(args))
    # ls
    elif command == commands[8]:
        ls(clientSocket, args, len(args))
    # open
    elif command == commands[9]:
        clientSocket = opens(clientSocket, args, len(args))
    # put
    elif command == commands[10]:
        put(clientSocket, args, len(args))
    # pwd
    elif command == commands[11]:
        pwd(clientSocket)
    # rename
    elif command == commands[13]:
        rename(clientSocket, args, len(args))
    # user
    elif command == commands[14]:
        user(clientSocket, args, len(args))