# IP Messenger — How to Run

This is a simple command-line IP Messenger implemented in Python. It lets you manage contacts and send XML-formatted chat messages over TCP.

## Prerequisites

* Python 3 installed on your system.
* (No extra packages required.)

## Running the Program

1. Open a terminal.

2. Navigate to the directory containing the `ip_messenger.py` script.

3. Run the messenger with:

```bash
python3 ip_messenger.py
```

4. Follow the prompts:

* Enter your username.
* Enter the port number to listen on (default is 12345).
* Use the commands listed to add contacts, send messages, etc.

## Basic Commands

* `add <name> <ip> [port]` — Add a new contact. Port is optional (default 12345).
* `remove <name>` — Remove a contact.
* `edit <name> <ip> [port]` — Edit contact info.
* `list` — Show all contacts.
* `send <name> <message>` — Send a message to a contact.
* `exit` — Quit the program.

## Example Usage

* Add a contact:

```
add Bob 192.168.1.10 12346
```

* Send a message:

```
send Bob Hello Bob!
```

## Running Multiple Instances

To chat with another user, run the messenger on two terminals/computers with different usernames and ports. Add each other as contacts using IP and port, then send messages.
