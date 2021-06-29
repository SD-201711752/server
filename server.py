import os
import requests
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
verifica = False
competicao = False
global auxiliar

info = {
    "componente": "server",
    "versao": "0.1",
    "descricao": "serve os clientes com os servicos disponilizados",
    "ponto_de_acesso": "https://sd-dmss.herokuapp.com",
    "status": "up",
    "identificacao": 2,
    "lider": False,
    "eleicao": "valentao",
    "servidores_conhecidos": [
        {
            "id": 1,
            "url": "https://sd-rdm.herokuapp.com"
        },
        {
            "id": 2,
            "url": "https://sd-201620236.herokuapp.com"
        },
        {
            "id": 3,
            "url": "https://sd-mgs.herokuapp.com"
        },
        {
            "id": 4,
            "url": "https://sd-jhsq.herokuapp.com/"
        },
        {
            "id": 5,
            "url": "https://sd-app-server-jesulino.herokuapp.com/"
        }
    ]
}

dadosEleicao = {
    "tipo_de_eleicao_ativa": info["eleicao"],
    "eleicao_em_andamento": False
}

dadosCoordenador = {
    "coordenador": 2,
    "id_eleicao": "o id da eleição"
}


@app.route('/info', methods=['GET', 'POST'])
def funInfo():
    global info
    if request.method == 'GET':
        return jsonify(info)
    elif request.method == 'POST':
        dados = request.get_json()
        try:
            if dados["status"] == "up" or dados["status"] == "down":
                info["status"] = dados["status"]
        except KeyError:
            pass
        try:
            if type(dados["identificacao"]) == int:
                info["identificacao"] = dados["identificacao"]
        except KeyError:
            pass
        try:
            if type(dados["lider"]) == bool:
                info["lider"] = dados["lider"]
        except KeyError:
            pass
        try:
            if dados["eleicao"] == "valentao" or dados["eleicao"] == "anel":
                info["eleicao"] = dados["eleicao"]
        except KeyError:
            pass
        return jsonify(info)


@app.route('/recurso', methods=['GET', 'POST'])
def estado():
    global verifica
    if request.method == 'GET':
        verifica = False
        operacao = 200
        return jsonify({"ocupado": verifica}), operacao
    elif request.method == 'POST':
        thr = threading.Thread(target=respFunc, args=())
        if verifica:
            operacao = 409
        else:
            verifica = True
            thr.start()
            operacao = 200
        return jsonify({"ocupado": verifica}), operacao


@app.route('/eleicao', methods=['GET', 'POST'])
def funEleicao():
    global dadosEleicao, competicao, info, auxiliar
    competicao = False
    listaThr = []
    if request.method == 'GET':
        return jsonify(info)
    elif request.method == 'POST':
        auxiliar = request.json["id"]
        if not dadosEleicao["eleicao_em_andamento"]:
            dadosEleicao["eleicao_em_andamento"] = True
            if dadosEleicao["tipo_de_eleicao_ativa"] == "valentao":
                for servidor in info["servidores_conhecidos"]:
                    listaThr.append(threading.Thread(target=valentao, args=(servidor["url"],)))
                    listaThr[-1].start()
                for i in range(len(listaThr)):
                    listaThr[i].join()
                if competicao is False:
                    requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                  json={"coordenador": dadosCoordenador["coordenador"],
                                        "id_eleicao": auxiliar})
            dadosEleicao["eleicao_em_andamento"] = False
        return jsonify({"id": auxiliar})


@app.route('/eleicao/coordenador', methods=['POST'])
def coord():
    global dadosCoordenador
    dados = request.get_json()
    dadosCoordenador["coordenador"] = dados["coordenador"]
    dadosCoordenador["id_eleicao"] = dados["id_eleicao"]
    return jsonify(dadosCoordenador)


def respFunc():
    global verifica
    time.sleep(10)
    verifica = False


def valentao(target):
    global competicao, info, auxiliar
    dados = requests.get(target + '/info').json()
    if dados["identificacao"] > info["identificacao"]:
        competicao = True
        requests.post(target + "/eleicao", json={"id": auxiliar})


def main():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)


main()
