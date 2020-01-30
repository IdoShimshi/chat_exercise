import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit, disconnect
from threading import Timer
import logging
from datetime import datetime


class ResettableTimer(object):
    # gives threading.Timer a reset option
    def __init__(self, time, func):
        self.__time = time
        self.__func = func
        self.__set()
        self.__running = False

    def __set(self):
        self.__timer = Timer(self.__time, self.__func,)

    def start(self):
        self.__running = True
        self.__timer.start()

    def cancel(self):
        self.__running = False
        self.__timer.cancel()

    def reset(self, start=False):
        if self.__running:
            self.__timer.cancel()
        self.__set()
        if self.__running or start:
            self.start()


class Client:
    # stores data about connected clients
    def __init__(self, user, sid, client_time):
        self.user = user
        self.sid = sid
        self.client_time = client_time
        self.activity_timer = ResettableTimer(60, self.disc_after_60)
        self.activity_timer.start()

    def disc_after_60(self):
        # disconnects user
        with app.test_request_context():
            with app.app_context():
                emit('message', ("SERVER", "Bye :)"), room=self.sid, namespace='/')
                print(f"{self.user} disconnected")
                log_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                logging.info(f'{log_time} - user : {self.user} disconnected due to inactivity')
                disconnect(self.sid, namespace='/')
                emit('message', ("SERVER", f"{self.user} has left the server!"), broadcast=True, namespace='/')
        del clients[self.user]


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
sio = SocketIO(app, async_mode="eventlet")

logging.basicConfig(level=logging.INFO, filename="server_log.log", format=f'%(levelname)s -  %(message)s')
log_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
logging.info(f"{log_time} - Server has started")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
clients = {}
print("Server has started")


@sio.on('register')
def handle_register(client_user, client_time):
    # creates a Client instance and notifies everyone a new client has connected
    print(f"{client_user} registered")
    log_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logging.info(f'{log_time} - user : {client_user} registered. client machine time - {client_time}')
    clients[client_user] = Client(client_user, request.sid, client_time)
    emit('message', ("SERVER", f"{client_user} has joined the server!"), broadcast=True)


@sio.on('message')
def handle_message(client_user, msg, client_time):
    # dispatches incoming message to relevant users
    clients[client_user].activity_timer.reset()
    print(f"{client_user}: {msg}")
    log_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    logging.info(f'{log_time} - user : {client_user} sent message - {msg}. client machine time - {client_time}')
    if msg[:4] == '/to ':
        clients[client_user].activity_timer.reset()
        to_length = msg[4:].find(' ')+4
        to_users = msg[4:to_length]
        msg = msg[to_length+1:]
        users = to_users.split(',')
        for user in users:
            try:
                emit('message', (client_user, msg), room=clients[user].sid)

            except KeyError:
                emit('message', ("SERVER", f"{user} is not a connected client!"), room=clients[client_user].sid)
            except Exception as e:
                print(e)
    else:
        emit('message', (client_user, msg), broadcast=True, include_self=False)


if __name__ == '__main__':
    sio.run(app)
