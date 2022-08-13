import json
import pickle
import socket
import threading
import subprocess
import pymysql as sql
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
from Chat_Configure import *
from sqlite_connect import Database

current_active_friend = ""


hostname = "127.0.0.1"
port = 1205
user_name = "Alok"
database_name = "Alok_client"
db = Database(database_name)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect(("127.0.0.1", 1205))


def ClickAction():
    """ this function callback  on the click of send button """
    EntryText = FilteredMessage(EntryBox.get("0.0", END))
    if EntryText == '':
        messagebox.showinfo("Info", "Please enter the message")
    else:
        EntryBox.delete("0.0", END)
        username = get_friend_list("user.json")
        # client_connection.send_msg(current_active_friend, username["dilip"], EntryText)
        comp_msg = {"sender": username[user_name], "recv": current_active_friend, "message": EntryText}
        # print (comp_msg)
        try:
            s.sendall(pickle.dumps(comp_msg))
            LoadMyEntry(EntryText, chat_display)
            db.insert_data(comp_msg)
        except OSError or BrokenPipeError:
            messagebox.showinfo("Info", "Server not responding \n unable to send the message")

        # byt = EntryText.encode()
        # print(byt)
        # s.sendall (byt)


def validate_contact(user_id):
    try:
        conn = sql.connect("localhost", "root", "dpyadav02$", "CHAT_MESSAGE")
        cursor = conn.cursor()
        result = cursor.execute("SELECT * FROM USER_INFO WHERE USER_ID LIKE '%s'" % user_id)
        return result
    except Exception as e:
        print(e)
        conn.close()


def pop_notification(message):
    friend = get_friend_list("friend_list.json")
    for name, u_id in friend.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if message['sender'] == u_id:
            subprocess.Popen(['notify-send', name+": "+message['message']])


def color_the_contact(msg_data):
    friend = get_friend_list("friend_list.json")
    for name, u_id in friend.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if msg_data['sender'] == u_id:
            index = list_box.get(0, "end").index(name)
            list_box.itemconfig(index, {'foreground': "#FF8000"})


def PressAction():
    """this function call after release  of enter button
     it change state of the entry box from disabled to normal"""
    EntryBox.config(state=NORMAL)
    ClickAction()


def DisableEntry():
    """ it change state of the entry box from normal to disabled"""
    EntryBox.config(state=DISABLED)


def sender_active(sender_id):
    if sender_id in current_active_friend:
        return True
    else:
        return False


def get_friend_list(filename):
    with open('data_files/%s' % filename, 'r+') as f:
        # print(f.read())
        data = json.load(f)
        return data


def save_account(username, user_id):
    """this function save the user name and id in the json file and update the contact list"""
    with open('data_files/friend_list.json', 'r+') as f:
        # print(f.read())
        data = json.load(f)
        data[username] = user_id     # <--- add `id` value.
        f.seek(0, 0)  # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()
        list_box.delete(0, END)
        create_list_of_contact()


def delete_contact():
    index = list_box.curselection()
    contact_name = list_box.get(index)
    import json

    with open('data_files/friend_list.json', 'r') as data_file:
        data = json.load(data_file)

        if contact_name in data:
            del data[contact_name]

    with open('data_files/friend_list.json', 'w') as data_file:
        data = json.dump(data, data_file)

    list_box.delete(0, END)
    create_list_of_contact()


def create_account():
    """this function get the value from textfield and callback the save account"""
    username = user.get()
    user_id = Id.get()
    if username == "" or user_id == "":
        messagebox.showinfo("ALERT", "Please enter the username and password")
        user.set("")
        Id.set("")
    else:
        duplicate = validate_contact(user_id)
        if duplicate > 0:
            contact_list = get_friend_list("friend_list.json")
            if username in contact_list or user_id in contact_list.values():
                messagebox.showinfo("ALERT", "Username OR Id already exist")
            else:
                user.set("")
                Id.set("")
                save_account(username, user_id)
                print(username, user_id)
        else:
            messagebox.showwarning("Alert", "No such contact exist")


def retrieve_message(current_user, current_friend):
    result = db.retrieve_data(current_user, current_friend)
    for msg in result:
        if msg[0] == "369852147":
            LoadMyEntry(msg[2], chat_display)
        else:
            LoadOtherEntry(chat_display,  msg[2])


def cur_select(evt):
    """this function callback when user select any of the contact list
    change to chat window"""
    print(evt)
    cur_sel = list_box.curselection()
    if cur_sel != ():
        value = str((list_box.get(cur_sel)))
        group['text'] = value
        global current_active_friend
        friend_list = get_friend_list("friend_list.json")
        current_active_friend = friend_list[value]
        list_box.itemconfig(cur_sel[0], {'foreground': "#000000"})
        shift_chat_window()
        user_list = get_friend_list("user.json")
        retrieve_message(user_list[user_name], current_active_friend)


def clean_msg():
    """clear all messages of the other user before starting the new user"""
    chat_display.configure(state=NORMAL)
    chat_display.delete("0.0", END)
    chat_display.configure(state=DISABLED)


def shift_chat_window():
    clean_msg()
    main_frame.grid_forget()
    chat_frame.grid(row=0, column=0, sticky=E + W + N + S)


def shift_list_window():
    global current_active_friend
    current_active_friend = ""
    chat_frame.grid_forget()
    main_frame.grid(row=0, column=0, sticky=W + E)


def create_list_of_contact():
    """create sorted  contact list of the """
    sorted_friend_list = {}
    friend_list = get_friend_list('friend_list.json')
    for key in sorted(friend_list.keys()):
        sorted_friend_list[key] = friend_list[key]

    for name, u_id in sorted_friend_list.items():
        list_box.insert(END, name)


root = Tk()
root.title(user_name)

sizex = 500
sizey = 700
posx = 40#ERTY
posy = 20
root.wm_geometry("%dx%d+%d+%d" % (sizex, sizey, posx, posy))

main_frame = Frame(root, background="#3B66A5")
main_frame.grid(row=0, column=0, sticky=W + E)

head = Label(main_frame, text='Chat_ON', font=('Elephant', 35), pady=10, foreground="#ffffff", background="#3B66A5")
head.grid(row=0, column=0)

list_box = Listbox(main_frame, width=60, height=10, font=("Elephant", 20), justify=CENTER)
list_box.bind('<Double-Button-1>', cur_select)
list_box.grid(row=1, column=0, padx=10, pady=10, sticky=E + W + N + S)
create_list_of_contact()

delete_button = Button(main_frame, text="Delete", width=10, height=1, font=("Elephant", 10), command=lambda: delete_contact())
delete_button.grid(row=2, column=0, padx=1, pady=1)

heading = Label(main_frame, text='Create Contact', font=('Elephant', 35), pady=10, foreground="#ffffff", background="#3B66A5")
heading.grid(row=3, column=0)

logf = Frame(main_frame, padx=10, pady=10, background="#3B66A5")
logf.grid(row=4, column=0)

user = StringVar()
Label(logf, text='Username: ', font=('', 20), pady=5, padx=5, foreground="#ffffff", background="#3B66A5").grid(sticky=W)
Entry(logf, textvariable=user, bd=5, font=('', 15)).grid(row=0, column=1)

Id = StringVar()
Label(logf, text='User_ID: ', font=('', 20), pady=5, padx=5, foreground="#ffffff", background="#3B66A5").grid(sticky=W)
Entry(logf, textvariable=Id, bd=5, font=('', 15)).grid(row=1, column=1)

Button(logf, text=' Save Account ', bd=3, font=('', 15), padx=5, pady=5, command=lambda: create_account()).grid()
# Button(logf, text=' Create Account ', bd=3, font=('', 15), padx=5, pady=5, command='self.cr').grid(row=2, column=1)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

"""========================================================================"""
chat_frame = Frame(root, background="#3B66A5")
# chat_frame.grid(row=0, column=0, sticky=E + W + N + S)

buttons_frame = Frame(chat_frame, background="#3B66A5")  # Create the Button frame to places the button
buttons_frame.grid(row=0, column=0, sticky=E + W + N + S)

btn_back = Button(buttons_frame, text='Back', command=shift_list_window)   # Back Button
btn_back.grid(row=0, column=0, padx=10, pady=10)

group = LabelFrame(chat_frame, text='', font=("Elephant", 20), padx=5, pady=5)
group.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=E + W + N + S)

chat_display = scrolledtext.ScrolledText(group, font=("Elephant", 12), width=40, height=25)
chat_display.configure(state=DISABLED)
chat_display.grid(row=0, column=0, sticky=E + W + N + S)

EntryFrame = Frame(chat_frame)
EntryFrame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky=E + W + N + S)

EntryBox = Text(EntryFrame, bd=0, bg="white", width="29", height="3", font=("Elephant", 16))

EntryBox.bind("<Return>", lambda event: DisableEntry())
EntryBox.bind("<KeyRelease-Return>", lambda event: PressAction())
EntryBox.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky=E + W + N + S)

SendButton = Button(EntryFrame, font=("Elephant", 15), text="Send", width="8", height=3, bd=0,
                    bg="#FFBF00", activebackground="#FACC2E", command=lambda: ClickAction())
SendButton.grid(row=0, column=3, padx=8, pady=10, sticky=E + W + N + S)

chat_frame.columnconfigure(0, weight=1)
chat_frame.rowconfigure(1, weight=1)

group.columnconfigure(0, weight=1)
group.rowconfigure(0, weight=1)

EntryFrame.columnconfigure(0, weight=1)
EntryFrame.rowconfigure(0, weight=1)


def receive_msg():
    database = Database(database_name)
    try:
        print("try to connect to the server")
        s.connect((hostname, port))
        print("connect")
        user_list = get_friend_list("user.json")
        print(user)
        s.sendall(pickle.dumps(user_list[user_name]))
    except Exception as e:
        print(e)
        # LoadConnectionInfo (ChatLog, '[ Unable to connect ]')
        return

    while True:

        try:
            data = s.recv(1024)
            decode_data = pickle.loads(data)
            # print("recv", pickle.loads(data))

        except Exception as e:
            print(e)
            # LoadConnectionInfo (ChatLog, '\n [ Your partner has disconnected ] \n')
            break
        if data != '':
            for msg_data in decode_data:
                playsound('notif.wav')
                database.insert_data(msg_data)
                # print("msg data", msg_data)
                if sender_active(msg_data["sender"]):
                    LoadOtherEntry(chat_display, msg_data['message'])
                else:
                    color_the_contact(msg_data)
                    pop_notification(msg_data)
        else:
            print("failed")
            # LoadConnectionInfo (ChatLog, '\n [ Your partner has disconnected ] \n')
    s.close()


thread = threading.Thread(target=receive_msg, daemon=True)
thread.start()
root.mainloop()
