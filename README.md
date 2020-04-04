# Bub-n-Bros

This is a fork of [Armin Rigo's HTML5 port](https://bitbucket.org/arigo/bub-n-bros) of the original
[Bub's Brothers](http://bub-n-bros.sourceforge.net/), ported to Python 3 since Python 2.x
is now end-of-life and with plans for other enhancements (see the Issues page).

## Reporting Issues

This project is work in progress and the Python 3 port especially is still extremely experimental.
Please report any issues you find on [the BitBucket Issue tracker](https://bitbucket.org/fpiesche/bub-n-bros/issues/)

## Requirements

  * Python 3.x (I personally develop and test on Python 3.7). On Windows, I recommend installing
  [Chocolatey](https://www.chocolatey.org/) to easily install Python 3 (`choco install python`).

## Installing

Download the repository from the *Downloads* section here on the BitBucket repository and extract it
to a directory of your choice. Open a Terminal window and navigate to this directory
(on Windows: simply enter `cmd` in the Explorer location bar when viewing the directory).

Create a Python virtual environment to run the server in:

`virtualenv ./venv`

Activate the virtual environment:

`source ./venv/bin/activate` (Linux/macOS)

`.\venv\Scripts\activate.bat` (Windows)

Install the requirements:

`pip install -f .\requirements.txt`

## Running the game

Open a Terminal and activate the virtual environment as above, then simply run:

`python bb_tornado.py --metaserver=none`

This will start a web server on your machine on port 8000 serving a game.

Simply visit http://127.0.0.1:8000 in a web browser to play.

Add players by clicking on the dragon of your choice on the left, and then pressing
four keys (right, left, jump, fire).

Any connection supports any number of players: you can add two or even three players
on the same keyboard on each connected computer, but it becomes crowded and keyboards
are usually prone to conflicts if a lot of keys are pressed simultaneously.

## Common command-line options

`--upnp=True` will automatically forward the game's port on your router so your friends
on the internet can join.

`--port=8000` allows you to set a custom port.

For more options see `python bb_tornado.py --help`.

## The Metaserver

The metaserver is a server that manages a list of running games so people can view and join
them from a central location. You can start a metaserver by running `python metaserver.py`.

Individual game servers can then add your metaserver's URL to their `--metaserver` command-line
to be listed there. There is currently no default metaserver.

## Acknowledgments

  * [Sebastian Wegner](http://www.mcsebi.com/) (original MacOS game "Bub & Bob" which many of the assets in Bub-n-Bros are from)
  * Armin Rigo ([original Python code](https://bub-n-bros.sourceforge.net) and
  [HTML5 port](https://bitbucket.org/arigo/bub-n-bros))
  * [Original Bub-n-Bros contributors](http://bub-n-bros.sourceforge.net/authors.html):
    * David Gowers (art)
    * Gio, Odie, Michel-Stéphane, Armin (levels)
    * Odie, Brachamutanda (special thanks)
    * IMA Connection (beta testing)
