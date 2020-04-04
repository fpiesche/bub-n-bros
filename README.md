# README #

### Bub-n-Bros ###

This is the HTML5 version of the Bub-n-Bros game, a many-players
version of the original Bubble Bobble game.


### How to run your own server ###

You need to have Python version 2.7 installed, as well as "pip", the
Python package manager.  (It is recommended to use "virtualenv" as
well, but not necessary.)

Install "tornado" by saying "pip install tornado".

Grab the source code here: go to
https://bitbucket.org/arigo/bub-n-bros/downloads , click on Tags,
click on one of "zip" or "gz" or "bz2".

Run "python bb_tornado.py --metaserver=none".

This should start a web server on the local machine, on port 8000,
serving a game (can be changed with the option --port=NUM).

Visit http://127.0.0.1:8000 in your regular web browser.

The server does not only listen from the local machine: you can also
add new connections from other machines, as long as you know the IP (or
maybe the DNS name) of the machine running the server.  (The
"127.0.0.1" above means "the local machine".)  The clients are purely
web-based applications; no need to install anything there.  In other
words a client is any (HTML5-compatible) web browser which connects to
the server.

Add players by clicking on the dragon of your choice on the left, and
then pressing four keys (right, left, jump, fire).

Any connection supports any number of players: you can add two or even
three players on the same keyboard, but it becomes crowded and
keyboards are usually prone to conflicts if a lot of keys are pressed
simultanously.

For more options see "python bb_tornato.py --help".  The metaserver is
a different machine, which is running "python metaserver.py", and
individual servers show up on the metaserver.  (There is no running
default metaserver right now.)
