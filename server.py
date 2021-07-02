import os
import requests
import threading
import time

from operator import itemgetter
from flask import Flask, jsonify, request

app = Flask(__name__)
verifica = False
competicao = False
auxiliar = ""

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
            "url": "https://sd-jhsq.herokuapp.com"
        },
        {
            "id": 5,
            "url": "https://sd-app-server-jesulino.herokuapp.com"
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
        return jsonify(dadosEleicao)
    elif request.method == 'POST':
        auxiliar = request.json["id"]
        if not dadosEleicao["eleicao_em_andamento"]:
            dadosEleicao["eleicao_em_andamento"] = True
            if dadosEleicao["tipo_de_eleicao_ativa"] == "valentao":
                for servidor in info["servidores_conhecidos"]:
                    valentao(servidor["url"])
                    time.sleep(1)
                if competicao is False:
                    requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                  json={"coordenador": dadosCoordenador["coordenador"],
                                        "id_eleicao": auxiliar})
                    for servidor in info["servidores_conhecidos"]:
                        threading.Thread(target=(lambda: requests.post(servidor["url"] + '/eleicao/coordenador',
                                                                       json={"coordenador": dadosCoordenador[
                                                                           "coordenador"],
                                                                             "id_eleicao": auxiliar}))).start()
            elif dadosEleicao["tipo_de_eleicao_ativa"] == "anel":
                id_list = []
                i = 0
                for servidor in info["servidores_conhecidos"]:
                    id_list.append((servidor["url"], -1))
                    listaThr.append(threading.Thread(target=anel, args=(servidor["url"], id_list, i)))
                    listaThr[-1].start()
                    i += 1
                for i in range(len(listaThr)):
                    listaThr[i].join()
                id_list.sort(key=itemgetter(1))
                for server_id in id_list:
                    if server_id[1] > dadosCoordenador["coordenador"]:
                        requests.post(server_id[0] + "/eleicao", json={"id": auxiliar + '-'
                                                                             + str(dadosCoordenador["coordenador"])})
                        return
                servidores_validos = []
                for i in id_list:
                    if i[1] > -1:
                        servidores_validos.append(i)
                if len(servidores_validos) == 0:
                    requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                  json={"coordenador": dadosCoordenador["coordenador"], "id_eleicao": auxiliar})
                else:
                    requests.post(servidores_validos[0][0] + "/eleicao", json={"id": auxiliar + '-' +
                                                                                     str(dadosCoordenador[
                                                                                             "coordenador"])})
        else:
            return jsonify(dadosEleicao), 409
        if info["lider"]:
            dadosEleicao["eleicao_em_andamento"] = False
        return jsonify({"id": auxiliar})


@app.route('/eleicao/coordenador', methods=['POST', 'GET'])
def coord():
    global dadosCoordenador, dadosEleicao, info
    if request.method == 'GET':
        return jsonify(dadosCoordenador)
    elif request.method == 'POST':
        dados = request.get_json()
        dadosCoordenador["coordenador"] = dados["coordenador"]
        dadosCoordenador["id_eleicao"] = dados["id_eleicao"]
        dadosEleicao["eleicao_em_andamento"] = False
        if dadosCoordenador["coordenador"] == info["identificacao"]:
            info["lider"] = True
        else:
            info["lider"] = False
        return jsonify(dadosCoordenador)


@app.route('/eleicao/reset', methods=['GET'])
def reset():
    global dadosCoordenador
    dadosCoordenador["coordenador"] = 0
    dadosCoordenador["id_eleicao"] = ''
    return jsonify(dadosCoordenador)


def respFunc():
    global verifica
    time.sleep(10)
    verifica = False


def valentao(url):
    global competicao, info, auxiliar
    resp = requests.get(url + "/info")
    dados = resp.json()
    try:
        if dados["identificacao"] > info["identificacao"] and dados["status"] == "up" and info["eleicao"] == "valentao":
            competicao = True
            requests.post(url + "/eleicao", json={"id": auxiliar})
            print("Perdeu para '%s' [%d]" % (url, dados["identificacao"]))
    except requests.ConnectionError:
        pass
    except KeyError:
        pass


def anel(target, id_list, i):
    try:
        dados = requests.get(target + "/info").json()
        if dados["status"] == "down":
            print(f"[DEBUG] Server '{target}' is down")
        elif dados["eleicao"] == "valentao":
            print(f"[DEBUG] Server '{target}' is using a different election type")
        else:
            id_list[i] = (target, dados["identificacao"])
            print(f"[DEBUG] Server '{target}' is valid")
            return
    except requests.ConnectionError:
        pass
    except KeyError:
        pass
    except TypeError:
        pass
    id_list[i] = (target, -1)


def main():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)


main()
