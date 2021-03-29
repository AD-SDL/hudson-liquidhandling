INSTALLATION

zeromq is generally installed by default, but here are some
untested installation commands. On hudson02, everythinng was
already installed.

# install at the system level
sudo apt-get install libzmq3-dev

# install at the application level
./Anaconda3-2020.11-Linux-x86_64.sh
pip install pyzmq


BASICS

--

receive.py
send.py

These two files are a basic hello world to messaging with
zeromq.

--

send_new_files.py
get_new_files.py

There is a send_new_files.py script that takes as input a
directory to look in, and a time in seconds. Files with
a modification date newer than the current time minus the
number of seconds provided as the argument. A manifest of
these files is created and sent to the message queue. This
script would run on hudson01.

There is a get_new_files.py script that looks for messages
in the message queue. This script would run on lambda6.

--

dirmon.py
manifest.py

These are support functions, dirmon provides a function to
look at files and their stats in a given directory, maifest.py
generates the manifest data structure

t_dirmon.py
t_manifest.py

These were simple test scripts used while coding the support
functions.

--
