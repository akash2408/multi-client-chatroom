import time
from tkinter import *
from PIL import Image, ImageTk
import socket
from time import sleep
import threading
import sys

c = socket.socket()
HOST = 'localhost'
PORT = 5000
HEADER = 1024


def connect_to_server():
    global c
    try:
        c.connect((HOST, PORT))
        welcomeScreen()
    except socket.error as msg:
        print('Connection error: ' + str(msg) + '. Retrying...')
        sleep(1)
        connect_to_server()


def navigateToChatScreen(tk):
    tk.destroy()
    chatScreen()


def exitApp(tk):
    c.send(bytes('exit', 'utf-8'))
    tk.destroy()


def welcomeScreen():

    def startfun(username, tk):
        global c
        if (len(username) == 0):
            return
        name = username
        c.send(bytes(name, 'utf-8'))
        navigateToChatScreen(tk)

    tk = Tk()
    tk.geometry("300x500")
    tk.minsize(300, 500)
    tk.maxsize(300, 500)
    tk.config(bg="white")

    resize_welcome_image = Image.open("welcome.png").resize((300, 250))

    welcomeImg = ImageTk.PhotoImage(resize_welcome_image)

    welcomeImage = Label(tk, image=welcomeImg, bg="white").place(x=0, y=0)
    user_name = Label(tk, text="Username :", bg="white").place(x=10, y=280)
    user_name_field = StringVar()
    userNameBox = Entry(tk, textvariable=user_name_field, font=('calibre', 10, 'normal'), border=2, width=28)

    userNameBox.place(x=80, y=280)

    startChatImage = Image.open("start.png")

    resize_chat_image = startChatImage.resize((100, 100))

    startChatImg = ImageTk.PhotoImage(resize_chat_image)

    startButton = Button(tk, image=startChatImg, command=lambda: startfun(user_name_field.get(), tk), borderwidth=0)
    startButton.place(x=90, y=350)
    tk.mainloop()


def chatScreen():
    tk = Tk()
    tk.geometry("300x500")
    tk.minsize(300, 500)
    tk.maxsize(300, 500)
    tk.config(bg="white")

    exitChatRoom = Image.open("exit.png")

    resize_exit_image = exitChatRoom.resize((150, 50))

    exitImg = ImageTk.PhotoImage(resize_exit_image)

    exitButton = Button(tk, image=exitImg, bg="white", command=lambda: exitApp(tk), borderwidth=0)
    exitButton.place(x=70, y=10)

    messageListBox = Listbox(tk, height=20, width=43)
    messageListBox.place(x=15, y=80)

    message = StringVar()
    messageBox = Entry(tk, textvariable=message, font=('calibre', 10, 'normal'), border=2, width=32)
    messageBox.place(x=15, y=444)

    sendMessageImage = Image.open("send.png")

    resize_send_image = sendMessageImage.resize((30, 30))

    sendImg = ImageTk.PhotoImage(resize_send_image)

    sendButton = Button(tk, image=sendImg, bg="white", command=lambda: send_message(message.get()), borderwidth=0)
    sendButton.place(x=250, y=440)

    def handle_message():
        global c
        while True:
            data = c.recv(HEADER).decode('utf-8')

            if data == 'exit':
                exit()
            messageListBox.insert(messageListBox.size(), data)
            print(data)

    def send_message(msg):
        global c
        if (len(msg) == 0):
            return

        c.send(bytes(msg, 'utf-8'))
        messageBox.delete(0, 'end')
        messageListBox.insert(messageListBox.size(), "You: " + msg)

    global t, t1
    t = threading.Thread(target=handle_message)
    t.start()
    t1 = threading.Thread(target=send_message(""))
    t1.start()
    tk.mainloop()

global t, t1
connect_to_server()
t1.join()
t.join()
c.close()
exit(0)