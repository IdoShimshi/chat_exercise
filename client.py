import socketio
from datetime import datetime
import configparser


def register_client():
    # connects and requests registration
    sio.connect('http://localhost:5000')
    current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
    sio.emit('register', (my_username, current_time))


def run_loop():
    # input loop, sends a message when entered
    while True:
        msg = input("")
        if msg:
            current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            sio.emit('message', (my_username, msg, current_time))


def get_username():
    # returns username either from config file or user input
    parser = configparser.ConfigParser()
    parser.read('config.ini')
    if len(parser) == 2:
        try:
            user = parser.get('chat_username', 'username')
        except Exception as e:
            print(e)
            print("config file incorrect, check readme for format")
            user = input("Please enter your username manually: ")
    else:
        user = input("Please enter your username: ")
    return user


my_username = get_username()
sio = socketio.Client()
sio.reconnection = False


@sio.event
def message(sender, data):
    print(f"{sender}: {data}")


@sio.event
def connect():
    print("I'm connected!")


@sio.event
def connect_error():
    print("The connection failed!")


@sio.event
def disconnect():
    print("I'm disconnected!")


register_client()
run_loop()
