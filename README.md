# chat_excersize
A simple terminal chat server and client excersize for AnyVision

HOW TO RUN:

run server.

run client.

client gets username from either a config.ini file if it exists or user input (see below for config format).

type any message and simply press enter to send to everyone connected.

to send to a spesific user add /to, followed by a space and a list of users to send to, and then the message. example:

"/to username1,username2,username3 hello part of the world"

after 60 seconds of inactivity, client is disconnected.

server will log to a server_log.log file.



config file:

config file name should be config.ini

config file should include the following:

[chat_username]

username = anyvision1
