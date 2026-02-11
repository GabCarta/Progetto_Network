from flask import Flask, jsonify, request
import time

app = Flask(__name__)

# temporary memory to storage message
MESSAGGI = []

@app.route('/api/messaggi', methods=['POST'])
def invia_messaggio():
    if not request.is_json:
        return jsonify({"errore": "Formato JSON richiesto"}), 400

    dati = request.get_json()
    mittente = dati.get('mittente', 'Anonimo')
    testo = dati.get('testo', '')

    # create message object with incremental ID
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
   # client request messages newer than a certain ID 
    da_id = request.args.get('da_id', default=-1, type=int)
    
   #filter list to return only new messages
    nuovi_messaggi = [m for m in MESSAGGI if m['id'] > da_id]
    
    return jsonify(nuovi_messaggi), 200

if __name__ == "__main__":
    #SSL context for HTTPS
    context = ('cert.pem', 'key.pem')

    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=context)