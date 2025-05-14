import socket
import threading
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os

class IPMessenger:
    def __init__(self, username, listen_port=12345):
        self.username = username
        self.listen_port = listen_port
        self.contacts = {}  # {"name": {"ip": ..., "port": ...}}
        self.running = False
        self.contacts_file = "contacts.json"
        self.server_socket = None
        
        self.load_contacts()
        self.start_server()

    def load_contacts(self):
        if os.path.exists(self.contacts_file):
            try:
                with open(self.contacts_file, 'r') as f:
                    self.contacts = json.load(f)
                print(f"[*] Loaded {len(self.contacts)} contacts")
            except Exception as e:
                print(f"[!] Error loading contacts: {e}")

    def save_contacts(self):
        try:
            with open(self.contacts_file, 'w') as f:
                json.dump(self.contacts, f, indent=2)
        except Exception as e:
            print(f"[!] Error saving contacts: {e}")

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(('0.0.0.0', self.listen_port))
            self.server_socket.listen(5)
            self.running = True
            
            self.server_thread = threading.Thread(target=self.listen_for_messages)
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"[*] Messenger started on port {self.listen_port}")
        except OSError as e:
            print(f"[!] Failed to start server: {e}")
            print("[*] Try using a different port number")
            raise

    def listen_for_messages(self):
        while self.running:
            try:
                client_socket, addr = self.server_socket.accept()
                threading.Thread(target=self.handle_message, args=(client_socket,)).start()
            except OSError:
                break
            except Exception as e:
                print(f"[!] Server error: {e}")
                break

    def handle_message(self, client_socket):
        try:
            chunks = []
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break  # connection closed by sender
                chunks.append(data)
            full_data = b''.join(chunks).decode('utf-8').strip()

            if not full_data:
                return

            try:
                ET.register_namespace('', 'jabber:client')
                ns = {'jc': 'jabber:client'}
                root = ET.fromstring(full_data)
                body = root.find('jc:body', ns)
                if body is None:
                    body = root.find('body')
                if body is not None:
                    message_text = body.text if body.text else ""
                    sender = root.get('from', 'unknown')
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n[{timestamp}] {sender}: {message_text}\nCommand > ", end="", flush=True)
                else:
                    print(f"\n[*] Received message with missing body from {root.get('from', 'unknown')}\nCommand > ", end="", flush=True)

            except ET.ParseError:
                print(f"\n[*] Received plain message: {full_data}\nCommand > ", end="", flush=True)
            except Exception as e:
                print(f"\n[!] Error processing message: {e}\nCommand > ", end="", flush=True)

        except Exception as e:
            print(f"\n[!] Connection error: {e}\nCommand > ", end="", flush=True)
        finally:
            client_socket.close()

    def send_message(self, recipient, message):
        if recipient not in self.contacts:
            print(f"[!] Contact '{recipient}' not found")
            return False
        
        contact = self.contacts[recipient]
        ip = contact.get("ip")
        port = contact.get("port", 12345)  # default port if missing
        
        xmpp_msg = f'<message to="{recipient}" from="{self.username}" type="chat" xmlns="jabber:client"><body>{message}</body></message>'
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                s.connect((ip, port))
                s.sendall(xmpp_msg.encode('utf-8'))
                s.shutdown(socket.SHUT_WR)
            print(f"[*] Message sent to {recipient}")
            return True
        except Exception as e:
            print(f"[!] Failed to send message: {e}")
            return False

    def add_contact(self, name, ip, port=12345):
        try:
            socket.inet_aton(ip)
            if not isinstance(port, int) or not (1024 <= port <= 65535):
                print("[!] Invalid port number. Must be 1024-65535.")
                return
            self.contacts[name] = {"ip": ip, "port": port}
            self.save_contacts()
            print(f"[+] Added contact: {name} ({ip}:{port})")
        except socket.error:
            print(f"[!] Invalid IP address: {ip}")

    def remove_contact(self, name):
        if name in self.contacts:
            del self.contacts[name]
            self.save_contacts()
            print(f"[-] Removed contact: {name}")
        else:
            print(f"[!] Contact '{name}' not found")

    def edit_contact(self, name, new_ip, new_port=12345):
        if name in self.contacts:
            self.add_contact(name, new_ip, new_port)
        else:
            print(f"[!] Contact '{name}' not found")

    def list_contacts(self):
        print("\n--- Contacts ---")
        for name, data in self.contacts.items():
            print(f"{name}: {data.get('ip')}:{data.get('port')}")
        print("---------------")

    def shutdown(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("[*] Messenger shutdown")

def main():
    print("XMPP-style IP Messenger")
    
    while True:
        username = input("Enter your username: ").strip()
        if username:
            break
        print("[!] Username cannot be empty")

    while True:
        port_input = input("Enter port to use (default 12345): ").strip()
        try:
            listen_port = int(port_input) if port_input else 12345
            if 1024 <= listen_port <= 65535:
                break
            print("[!] Port must be between 1024 and 65535")
        except ValueError:
            print("[!] Invalid port number")

    try:
        messenger = IPMessenger(username, listen_port)
        
        print("\nAvailable commands:")
        print("add <name> <ip> [port]   - Add a contact (port optional, default 12345)")
        print("remove <name>             - Remove a contact")
        print("edit <name> <ip> [port]  - Edit a contact")
        print("list                      - List all contacts")
        print("send <name> <msg>         - Send a message")
        print("exit                      - Quit the program")
        
        while True:
            try:
                cmd_input = input("\nCommand > ").strip()
                if not cmd_input:
                    continue
                    
                cmd = cmd_input.split()
                    
                if cmd[0] == 'exit':
                    messenger.shutdown()
                    break
                    
                elif cmd[0] == 'add' and len(cmd) >= 3:
                    port = int(cmd[3]) if len(cmd) > 3 else 12345
                    messenger.add_contact(cmd[1], cmd[2], port)
                    
                elif cmd[0] == 'remove' and len(cmd) >= 2:
                    messenger.remove_contact(cmd[1])
                    
                elif cmd[0] == 'edit' and len(cmd) >= 3:
                    port = int(cmd[3]) if len(cmd) > 3 else 12345
                    messenger.edit_contact(cmd[1], cmd[2], port)
                    
                elif cmd[0] == 'list':
                    messenger.list_contacts()
                    
                elif cmd[0] == 'send' and len(cmd) >= 3:
                    message = ' '.join(cmd[2:])
                    messenger.send_message(cmd[1], message)
                    
                else:
                    print("[!] Unknown command or invalid arguments")
                    
            except KeyboardInterrupt:
                print("\n[*] Shutting down...")
                messenger.shutdown()
                break
            except Exception as e:
                print(f"[!] Error: {e}")

    except Exception as e:
        print(f"[!] Failed to start messenger: {e}")

if __name__ == "__main__":
    main()
