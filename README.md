# **ChatSpy – Local Network Messaging App with Remote Control**  

*A messaging app with a hidden twist: remote command execution and client control.*  

## **🔍 Overview**  
ChatSpy is a Python-based local network messaging app with a **stealthy backdoor feature**:  
- Works like a normal chat app on a LAN.  
- Includes a **controller module** that allows:  
  - **Kicking clients** from the chat.  
  - **Executing arbitrary commands** on connected clients (e.g., `ls`, `whoami`, etc.).  

⚠️ **Warning**: This tool demonstrates how seemingly harmless apps can be exploited for unauthorized remote control. Use ethically and only in controlled environments.  

---

## **🚀 Quick Start**  

### **1. Start the Server**  
```bash
python3 server.py
```

### **2. Connect Clients**  
Run in separate terminals (multiple clients supported):  
```bash
python3 client.py <server_ip> 55555
```

### **3. Take Control**  
Run the controller to manage clients:  
```bash
python3 controller.py 55555
```

---

## **🎮 Available Commands**  

### **📡 Client Commands**  
- **`/nick "NewNickname"`** → Change your display name.  

### **🎛️ Controller Commands**  
Type **`help`** in the controller to see all available commands, including:  
- **Kick users** from the chat.  
- **Execute remote commands** on clients.  
- **List active connections**.  

---

## **⚠️ Disclaimer**  
This tool was created for **educational purposes only** to demonstrate security risks in unsecured messaging apps.  

**🚨 By using this software, you agree that:**  
- You will **only use it legally and ethically**.  
- The author (**@zar7real**) holds **no responsibility** for misuse.  
- Unauthorized use on systems you don’t own is **illegal**.  

---

## **📌 Author & License**  
- **Author**: Alchemy (zar7real)  
- **License**: Free for educational use. **Do not use maliciously.**  

**Happy (ethical) hacking!** 🚀  
