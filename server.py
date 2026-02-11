from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# Memoria temporanea dei messaggi (in una app vera useresti un Database)
# Formato: {'id': 0, 'mittente': 'Mario', 'testo': 'Ciao', 'timestamp': ...}
MESSAGGI = []

@app.route('/api/messaggi', methods=['POST'])
def invia_messaggio():
    if not request.is_json:
        return jsonify({"errore": "Formato JSON richiesto"}), 400

    dati = request.get_json()
    mittente = dati.get('mittente', 'Anonimo')
    testo = dati.get('testo', '')

    # Creiamo il messaggio con un ID progressivo
    nuovo_msg = {
        'id': len(MESSAGGI),
        'mittente': mittente,
        'testo': testo,
        'timestamp': time.time()
    }
    
    MESSAGGI.append(nuovo_msg)
    print(f"[SERVER] Nuovo messaggio da {mittente}: {testo}")
    
    return jsonify({"esito": "OK", "id": nuovo_msg['id']}), 201

@app.route('/api/messaggi', methods=['GET'])
def leggi_messaggi():
    # Il client ci dice: "Dammi i messaggi successivi all'ID X"
    # Esempio: /api/messaggi?da_id=5
    da_id = request.args.get('da_id', default=-1, type=int)
    
    # Filtriamo la lista per prendere solo i NUOVI messaggi
    # Se da_id è -1, li prende tutti (utile all'avvio)
    nuovi_messaggi = [m for m in MESSAGGI if m['id'] > da_id]
    
    return jsonify(nuovi_messaggi), 200

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    # host='0.0.0.0' permette connessioni da altri PC nella rete locale
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=context)