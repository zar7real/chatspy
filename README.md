# chatspy
This is a messaging app that works on local network except it has one cool little feature.

basically how this app works, you start the server, connect the clients and once that's done you just have to open another terminal and run the "controller.py" file, with it you can eject clients from the chat + execute arbitrary commands on the clients (like ls or whoami etc. etc.)

how to use:

1) first of all we start the server:

python3 server.py

2) then we run the clients (you can do it from multiple terminals):

python3 client.py <server_ip> 55555

3) then we run the controller:

python3 controller.py 55555

commands:

CLIENT COMMAND:
/nick "new nickname"

CONTROLLER COMMANDS:
type help and watch them lol

disclaimer: I am the author and I have no responsibility for how you use this tool. So if you do something stupid, don't bother me, the responsibility is yours and only yours. I created it to show how certain messaging apps can spy on users in an unwanted way.

