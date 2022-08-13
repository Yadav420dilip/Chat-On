import pickle
import selectors
import socket
import types
import pymysql as sql

hostname = "127.0.0.1"                                           # Server Hostname Name
port = 1205                                                             # port to communicate with the server
database_host = "127.0.0.1"                                    # database host name
user = 'root'                                                            # database username name
password = 'dpyadav02$'                                        # database password
db_name = 'CHAT_MESSAGE'                                 # database name
client_list = {}                                                        # list of currently connected users with server
sel = selectors.DefaultSelector()                            # selector object to store the socket event
error = ""


def find_pending_msg(receiver):
    """
    this function retrieve the pending message when the receiver comes online
    :param:receiver
    :return:
    """
    global db_conn, error
    try:
        db_conn = sql.connect(database_host, user, password, db_name)
        cursor = db_conn.cursor()
        cursor.execute("call Fetch_Pending_Msg(%s)" % receiver)
        result = cursor.fetchall()
        print(result)
        return result
    except Exception as error:
        print(error)
    finally:
        db_conn.close()


def insert_pending_msg(msg):
    """
    this function insert message when the receiver user is not online
    :param msg:
    :return:
    """
    global db_conn, error
    try:
        print("inserting data in database", msg)
        db_conn = sql.connect(hostname, user, password, db_name)
        cursor = db_conn.cursor()
        query = """INSERT INTO PENDING_MESSAGE(`SENDER_ID`, `RECEIVER_ID`, `MESSAGE`) VALUES('%s', '%s', '%s')""" \
                % (msg["sender"], msg["recv"], msg["message"])
        result = cursor.execute(query)
        db_conn.commit()
        print(result)
    except Exception as error:
        db_conn.rollback()
        db_conn.close()
        print(error)
    finally:
        db_conn.close()


def encode_data(data):
    """
    encode the dictionary
    :param data:
    :return: encrypted form of the dictionary message
    """
    return pickle.dumps(data)


def decode_data(data):
    """
    decrypt the dictionary message
    :param data:
    :return: decrypt the message into dictionary message
    """
    return pickle.loads(data)


def receiver_id(message):
    """
    find the receiver id into the message
    :param message:
    :return: receiver id
    """
    msg = pickle.loads(message)
    return msg["recv"]


def conver_list_dict(data):
    """
    it convert the list message from database into the dictionary
    list_message=[sender_id,recive_id,message]
    dict_message={"sender_id":value, "receiver_id":value, "message": value }
    :param data:
    :return: my list
    """
    mylist = list()
    if data is not None:
        for msg_data in data:
            mydict = dict()
            mydict["sender"] = msg_data[0]
            mydict["recv"] = msg_data[1]
            mydict["message"] = msg_data[2]
            mylist.append(mydict)
        return mylist
    else:
        return


def append_msg_recv_outb(recv_data):
    recv_key = client_list[recv_data["recv"]]
    recv_data_obj = recv_key.data
    recv_data_obj.outb.append(recv_data)
    pass


def accept_connection(sock_obj):
    """
    :param sock_obj:
    :return:
    """
    global error
    try:
        conn, addr = sock_obj.accept()  # Should be ready to read
        print('accepted connection from', addr)
        # conn.setblocking(False)
        user_id = pickle.loads(conn.recv(1024))          # receive id of the connected user
        print("new connected user id", user_id)

        data = types.SimpleNamespace(addr=addr, id=user_id, no_of_call=0,  inb=list(), outb=list())
        event = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, event, data=data)
    except Exception as error:
        print(error)


def service_connection(key_obj, event_mask):
    """
        this function provide  the service to the client
        --> receive the message and send to the other user
        :param key_obj:
        :param event_mask:
   """
    global error
    sock = key_obj.fileobj  # key_obj.fileobj is the socket object
    data = key_obj.data     # key_obj.data contain sending data

    if data.no_of_call == 0:
        """this condition check whether socket comes first time or multiple time"""

        global client_list
        client_list[data.id] = key_obj  # register the socket object with client id
        data.no_of_call = 1
        print("client_list", client_list)
        pending_msg = conver_list_dict(find_pending_msg(data.id))
        # retrieve the pending message from the database  for current user
        if pending_msg is not None:
            for msg in pending_msg:  # append the re
                data.outb.append(msg)

    else:
        if event_mask & selectors.EVENT_READ:
            # if the socket is ready for reading, then mask & selectors.EVENT_READ is true
            try:
                recv_data = sock.recv(1024)  # Should be ready to read
                if recv_data:   # if the data is received the provide the service else close the connection
                    recv_data = decode_data(recv_data)
                    if recv_data["recv"] in client_list:
                        append_msg_recv_outb(recv_data)
                    else:
                        insert_pending_msg(recv_data)
                else:
                    print('closing connection to...', data.addr)
                    if len(data.outb) != 0:
                        for outb_msg in data.outb:
                            insert_pending_msg(outb_msg)

                    client_list.pop(data.id)
                    sel.unregister(sock)
                    sock.close()
                    print("Successfully close the connection")
            except Exception as error:
                print(error)

        if event_mask & selectors.EVENT_WRITE:  # Should be ready to write
            if data.outb:
                try:
                    print('send message', repr(data.outb), 'to', data.addr)
                    sock.sendall(encode_data(data.outb))  # Should be ready to write
                    #   data.outb = data.outb[sent:]
                    data.outb = list()
                except Exception as error:
                    print(error)


"""====================================================================================="""
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((hostname, port))
        print("waiting for new connection..............")
        print('listening on', (hostname, port))
        s.listen(5)
        s.setblocking(False)
        sel.register(s, selectors.EVENT_READ, data=None)
        # listening socket was registered for the event selectors.EVENT_READ
    except Exception as e:
        print(e)

    while True:
        """
        sel.select(timeout=None) blocks until there are sockets ready for I/O. It returns a list of (key,events) tuples,
        one for each socket. key is a SelectorKey namedtuple that contains a fileobj attribute. key.fileobj is the
         socket object, and mask is an event mask of the operations that are ready.
        """
        try:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_connection(key.fileobj)
                else:
                    service_connection(key, mask)
        except KeyboardInterrupt as error:
            print(error)
