import socket
import threading
import sys
import select
import json

class ClientController:
    def __init__(self, server_ip, control_port=4343):
        self.server_ip = server_ip
        self.control_port = control_port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.current_output = ""
        self.command_lock = threading.Lock()

    def connect_to_server(self):
        try:
            self.control_socket.connect((self.server_ip, self.control_port))
            print(f"Connesso al server di controllo su {self.server_ip}:{self.control_port}")
            
            # Thread per ricevere i messaggi dal server
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # Mostra la lista iniziale dei client
            self.send_command("refresh")
            
            # Avvia l'interfaccia utente
            self.command_interface()
            
        except ConnectionRefusedError:
            print(f"Impossibile connettersi al server {self.server_ip}:{self.control_port}")
        except Exception as e:
            print(f"Errore: {str(e)}")
        finally:
            self.control_socket.close()

    def receive_messages(self):
        while self.running:
            try:
                ready, _, _ = select.select([self.control_socket], [], [], 0.1)
                if ready:
                    data = self.control_socket.recv(4096).decode('utf-8')
                    if not data:
                        break
                    
                    # Gestione messaggi JSON per output strutturati
                    if data.startswith("{") and data.endswith("}"):
                        try:
                            message = json.loads(data)
                            if message.get("type") == "command_result":
                                self.display_command_result(message)
                                continue
                        except json.JSONDecodeError:
                            pass
                    
                    self.current_output = data
                    self.display_output()
            except Exception as e:
                print(f"\nErrore nella ricezione: {str(e)}")
                break

    def display_output(self):
        """Mostra output normale"""
        with self.command_lock:
            print("\n" + "-"*50)
            print(self.current_output)
            print("-"*50 + "\n> ", end="", flush=True)

    def display_command_result(self, message):
        """Mostra output formattato per risultati comandi"""
        with self.command_lock:
            print("\n" + "="*50)
            print(f"Risultato comando sul client {message.get('client')}:")
            print("-"*50)
            print(message.get("output", "Nessun output"))
            print("="*50 + "\n> ", end="", flush=True)

    def send_command(self, command):
        try:
            self.control_socket.send(command.encode('utf-8'))
        except Exception as e:
            print(f"Errore nell'invio del comando: {str(e)}")

    def command_interface(self):
        while self.running:
            try:
                command = input("> ").strip()
                
                if not command:
                    continue
                    
                if command.lower() == 'exit':
                    self.running = False
                    break
                elif command.lower() == 'refresh':
                    self.send_command("refresh")
                elif command.lower().startswith('kick '):
                    self.handle_kick_command(command)
                elif command.lower().startswith('exec '):
                    self.handle_exec_command(command)
                elif command.lower() == 'help':
                    self.show_help()
                else:
                    print("Comando non riconosciuto. Digita 'help' per la lista comandi")
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                print(f"Errore: {str(e)}")

    def handle_kick_command(self, command):
        parts = command.split(' ', 1)
        if len(parts) == 2 and parts[1].strip():
            client_name = parts[1].strip()
            self.send_command(f"kick {client_name}")
        else:
            print("Formato comando errato. Usa: kick <nome>")

    def handle_exec_command(self, command):
        parts = command.split(' ', 2)
        if len(parts) == 3 and parts[1].strip() and parts[2].strip():
            client_num = parts[1].strip()
            cmd = parts[2].strip()
            
            # Verifica che client_num sia un numero
            if not client_num.isdigit():
                print("Il numero client deve essere un valore numerico")
                return
                
            self.send_command(f"exec {client_num} {cmd}")
        else:
            print("Formato comando errato. Usa: exec <num> <comando>")

    def show_help(self):
        help_text = """
        Comandi disponibili:
        refresh - Aggiorna lista client
        exec <num> <cmd> - Esegui comando sul client specificato
        kick <nome> - Disconnette il client specificato
        help - Mostra questo messaggio
        exit - Esci dal controller
        """
        print(help_text)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Utilizzo: python controller.py <server_ip>")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    controller = ClientController(server_ip)
    controller.connect_to_server()
