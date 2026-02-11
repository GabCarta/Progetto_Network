import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
import requests
import urllib3
import threading
import time
from datetime import datetime

# disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# configuration
SERVER_URL = "https://localhost:5000/api/messaggi"
CERT_PATH = "cert.pem"

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat SSL")
        self.root.geometry("450x650")
        
        # start variables
        self.ultimo_id_letto = -1
        self.stop_threads = False
        self.mio_nome = ""

        # start login flow
        self.chiedi_nickname()

    def chiedi_nickname(self):
        self.mio_nome = simpledialog.askstring("Login", "Scegli il tuo Nickname:")
        if not self.mio_nome:
            self.root.destroy() #exit if no nickname provided
            return
        
        self.costruisci_interfaccia()
        
        # start  background 
        self.thread_ascolto = threading.Thread(target=self.loop_ascolto_messaggi, daemon=True)
        self.thread_ascolto.start()

    def costruisci_interfaccia(self):
       # Header
        header_frame = tk.Frame(self.root, bg="#075E54", height=50)
        header_frame.pack(fill=tk.X)
        
        lbl_titolo = tk.Label(header_frame, text="Chat SSL Sicura", fg="white", bg="#075E54", font=("Helvetica", 12, "bold"))
        lbl_titolo.pack(pady=(5, 0))
        
        lbl_utente = tk.Label(header_frame, text=f"Loggato come: {self.mio_nome}", fg="#dcf8c6", bg="#075E54", font=("Helvetica", 9))
        lbl_utente.pack(pady=(0, 5))

        #Area Chat
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', bg="#ECE5DD", font=("Helvetica", 10))
        self.chat_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        #Incoming messages on the left
        self.chat_area.tag_config('other', foreground='black', background='white', 
                                  lmargin1=10, lmargin2=10, rmargin=50, wrap='word')
        
        # another message on the right
        self.chat_area.tag_config('me', justify='right', foreground='black', background='#DCF8C6', 
                                  lmargin1=50, lmargin2=50, rmargin=10, wrap='word')
        
        # timestamp and status
        self.chat_area.tag_config('info_dx', justify='right', foreground='gray', font=("Arial", 8))
        self.chat_area.tag_config('info_sx', justify='left', foreground='gray', font=("Arial", 8))

        # Text Area
        input_frame = tk.Frame(self.root, bg="#f0f0f0")
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.txt_messaggio = tk.Entry(input_frame, font=("Helvetica", 11))
        self.txt_messaggio.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        self.txt_messaggio.bind("<Return>", lambda event: self.invia_messaggio()) # Invio con tasto Enter

        btn_invia = tk.Button(input_frame, text="Invia ➤", bg="#128C7E", fg="white", 
                              command=self.invia_messaggio, font=("Helvetica", 10, "bold"))
        btn_invia.pack(side=tk.RIGHT)

    def aggiungi_bolla_chat(self, mittente, testo, is_me):
        
        self.chat_area.config(state='normal') # enable editing temporarily
        
        orario = datetime.now().strftime("%H:%M")
        
        if is_me:
            
            testo_formattato = f"\n {testo} \n"
            info_formattata = f"{orario} ✓✓ \n" 
            self.chat_area.insert(tk.END, testo_formattato, 'me')
            self.chat_area.insert(tk.END, info_formattata, 'info_dx')
        else:
            
            testo_formattato = f"\n [{mittente}]:\n {testo} \n"
            info_formattata = f"{orario} \n"
            self.chat_area.insert(tk.END, testo_formattato, 'other')
            self.chat_area.insert(tk.END, info_formattata, 'info_sx')

        self.chat_area.see(tk.END) # auto-scroll 
        self.chat_area.config(state='disabled') # Make read-only again

    def invia_messaggio(self):
        testo = self.txt_messaggio.get()
        if not testo.strip():
            return

        payload = {"mittente": self.mio_nome, "testo": testo}
        
        # Run network request in a separate thread to avoid freezing the UI
        def _request_invio():
            try:
                requests.post(SERVER_URL, json=payload, verify=CERT_PATH, timeout=5)
               # Clear input field on success
                self.root.after(0, lambda: self.txt_messaggio.delete(0, tk.END))
            except Exception as e:
                print(f"Errore invio: {e}")
                self.root.after(0, lambda: messagebox.showerror("Errore", "Impossibile inviare il messaggio al server"))

        threading.Thread(target=_request_invio, daemon=True).start()

    def loop_ascolto_messaggi(self):
        while not self.stop_threads:
            try:
                params = {'da_id': self.ultimo_id_letto}
                response = requests.get(SERVER_URL, params=params, verify=CERT_PATH, timeout=5)
                
                if response.status_code == 200:
                    messaggi = response.json()
                    for msg in messaggi:
                        # refresh ID
                        self.ultimo_id_letto = max(self.ultimo_id_letto, msg['id'])
                        
                        is_me = (msg['mittente'] == self.mio_nome)
                        
                        
                        self.root.after(0, self.aggiungi_bolla_chat, msg['mittente'], msg['testo'], is_me)
                
                time.sleep(1) # Polling every second
            except Exception as e:
                print(f"Errore connessione: {e}")
                time.sleep(2)

    def on_close(self):
        self.stop_threads = True
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    #Handle window close event
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()