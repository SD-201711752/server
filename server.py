from flask import Flask, jsonify, request
from threading import Thread
import threading
import time
import os


app = Flask(__name__)
verifica = False


@app.route('/info')
def get_json():
    return jsonify({
        "componente": "server",
        "versao": "0.1",
        "descricao": "serve os clientes com os servicos X, Y e Z",
        "ponto_de_acesso": "https://meu-app-sd.heroku.com",
        "status": "up",
        "identificacao": 2,
        "lider": 0,
        "eleicao": "valentao",
        "servidores_conhecidos": [
            {
                "id": "id_server_1",
                "url": "url_server_1"
            },
            {
                "id": "id_server2",
                "url": "url_server2"
            }
        ]
    })


@app.route('/recurso', methods=['GET', 'POST'])
def estado():
    global verifica
    thr = threading.Thread(target=respFunc, args=())
    if verifica:
        value = 409
    else:
        verifica = True
        thr.start()
        value = 200
    return jsonify({"ocupado": verifica}), value


def respFunc():
    global verifica
    time.sleep(10)
    verifica = False


def main():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)


main()
