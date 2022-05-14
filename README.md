# ARPSPOOFER

Script written in Python to do ARP poisoning.
To use it you need to be root or sudo privileges.

******

## How to install

Download the repository from git
`git clone <repo> && cp arpspoofer/`
install the requirements
`pip3 install -r requirements.txt`.

******

## How to run

You must open two terminal, or use terminator and open two panel,
in the first one spoof your fist target:
`sudo arpspoofer.py -t <target IP> -d <destination IP>`
in the other one you just switch the two IPs.
Now all the traffics will be share with you.

*An example to how to run the script*
![](gif/arpspoofer.gif)

******

