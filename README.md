## CS4032 - Lab 2 - David Doyle

This script requires both python 2.7 and pip to be installed on the machine running it.

### Compiling
There is no compiling required for this python script. Instead, the required *compile.sh* script installs a module required by this program, namely *futures*, using pip. The sole command executed within the *compile.sh* script is:
`pip install futures`

In order to run the script, give it permission to execute with `sudo chmod u+x compile.sh` and run:
`./compile.sh`

### Running
The server can be run by running the *start.sh* script provided and including a port number for the server to bind to:
`start.sh <port-number>`
