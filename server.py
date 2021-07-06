import os
import requests
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
verifica = False
competicao = True
estado = False
lista = []
participantes = []
auxiliar = ""

info = {
    "componente": "server",
    "versao": "0.1",
    "descricao": "serve os clientes com os servicos disponilizados",
    "ponto_de_acesso": "https://sd-dmss.herokuapp.com",
    "status": "up",
    "identificacao": 1,
    "lider": False,
    "eleicao": "valentao",
    "servidores_conhecidos": [
        {
            "id": 2,
            "url": "https://sd-201620236.herokuapp.com"
        },
        {
            "id": 3,
            "url": "https://sd-rdm.herokuapp.com"
        },
        {
            "id": 4,
            "url": "https://sd-app-server-jesulino.herokuapp.com"
        },
        {
            "id": 5,
            "url": "https://sd-jhsq.herokuapp.com"
        },
        {
            "id": 9,
            "url": "https://sd-mgs.herokuapp.com"
        }
    ]
}

dadosCoordenador = {
    "coordenador": "",
    "id_eleicao": "o id da eleição"
}

dadosEleicao = {
    "tipo_de_eleicao_ativa": "valentao",
    "eleicao_em_andamento": estado
}


@app.route('/info', methods=['GET', 'POST'])
def funInfo():
    global info, dadosEleicao
    if request.method == 'POST':
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
            if type(dados["lider"]) == bool or dados["lider"] in [0, 1]:
                info["lider"] = dados["lider"]
        except KeyError:
            pass
        try:
            if dados["eleicao"] == "valentao" or dados["eleicao"] == "anel":
                info["eleicao"] = dados["eleicao"]
                dadosEleicao["tipo_de_eleicao_ativa"] = dados["eleicao"]
                
        except KeyError:
            pass
        return jsonify(info)
    elif request.method == 'GET':
        return jsonify(info)


@app.route('/recurso', methods=['GET', 'POST'])
def funEstado():
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


def valentao(url):
    global competicao
    dados = requests.get(url + '/info').json()
    try:
        if dados["identificacao"] > info["identificacao"] and dados["status"] == "up" and dados[
            "eleicao"] == "valentao":
            competicao = True
            requests.post(url + "/eleicao", json={"id": auxiliar})
    except TypeError:
        pass


def anel(url):
    global lista
    try:
        dados = requests.get(url + "/info").json()
        if dados["status"] == "down" or dados["eleicao"] == "valentao":
            print(f"Servidor: '{url}' invalido")
        else:
            lista.append((url, dados["identificacao"]))
            print(f"Servidor '{url}' valido")
            return
    except requests.ConnectionError:
        pass
    except KeyError:
        pass
    except TypeError:
        pass


@app.route('/eleicao', methods=['GET', 'POST'])
def funEleicao():
    global dadosEleicao, competicao, auxiliar, participantes, estado, lista, info
    if request.method == 'POST':
        try:
            cont = 0
            competicao = False
            print(info["eleicao"])
            print(estado)
            print(request.json["id"])
            print(dadosEleicao["tipo_de_eleicao_ativa"])
            print(dadosEleicao["tipo_de_eleicao_ativa"] == "anel")
            if not estado:
                if type(request.json["id"]) is not int:
                    estado = True
                    if dadosEleicao["tipo_de_eleicao_ativa"] == "valentao":
                        auxiliar = request.json["id"]
                        for servidor in info["servidores_conhecidos"]:
                            valentao(servidor["url"])
                            time.sleep(1)
                        if competicao is False:
                            requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                          json={"coordenador": info["identificacao"],
                                                "id_eleicao": auxiliar})
                            for servidor in info["servidores_conhecidos"]:
                                requests.post(servidor["url"] + '/eleicao/coordenador',
                                              json={"coordenador": info["identificacao"],
                                                    "id_eleicao": auxiliar})
                    elif dadosEleicao["tipo_de_eleicao_ativa"] == "anel":
                        for servidor in info["servidores_conhecidos"]:
                            print(servidor["url"])
                            anel(servidor["url"])
                        print(lista)
                        lista.append((info["ponto_de_acesso"], info["identificacao"]))
                        listaServidores = sorted(lista, key=lambda x: x[1])
                        print(listaServidores)
                        if 'participantes' in request.json:
                            dados = request.json
                            participantes.append(dados["participantes"])
                            for servidor in listaServidores:
                                cont += 1
                                if servidor[1] > info["identificacao"]:
                                    requests.post(servidor[0] + "/eleicao",
                                                  json={"id": dados["id"],
                                                        "participantes": participantes})
                                    break
                                elif len(listaServidores) == cont and len(listaServidores) > 1:
                                    requests.post(listaServidores[0][0] + "/eleicao",
                                                  json={"id": dados["id"],
                                                        "participantes": participantes})
                        else:
                            auxiliar = request.json["id"]
                            print(info["identificacao"])
                            for servidor in listaServidores:
                                cont += 1
                                if servidor[1] > info["identificacao"]:
                                    requests.post(servidor[0] + '/eleicao', json={"id": auxiliar + '-'
                                                                                        + str(info["identificacao"])})
                                    return jsonify({"id": auxiliar + '-' + str(info["identificacao"])})
                                elif len(listaServidores) == cont:
                                    requests.post(listaServidores[0][0] + '/eleicao', json={"id": auxiliar + '-'
                                                                                                  + str(
                                        info["identificacao"])})
                                    return jsonify({"id": auxiliar + '-' + str(info["identificacao"])})
                    else:
                        return jsonify({"id":"erro"}), 409
                else:
                    return jsonify({"id": "erro - tipo invalido"}), 409
            elif info["eleicao"] == "anel" and estado is True:
                if "participantes" in request.json and info["identificacao"] in request.json["participantes"]:
                    dados = request.json
                    participantes.append(dados["participantes"])
                    auxiliar = dados["id"]
                    participantes.sort()
                    requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                  json={"coordenador": participantes[len(participantes) - 1],
                                        "id_eleicao": auxiliar})
                    for servidor in info["servidores_conhecidos"]:
                        requests.post(servidor["url"] + '/eleicao/coordenador',
                                      json={"coordenador": participantes[len(participantes) - 1],
                                            "id_eleicao": auxiliar})
                elif "participantes" in request.json:
                    participantes = request.json["participantes"]
                    participantes.append(info["identificacao"])
                    participantes.sort()
                    for i in participantes:
                        cont += 1
                        if i > info["identificacao"]:
                            for j in info["servidores_conhecidos"]:
                                if j["id"] == i:
                                    requests.post(j["url"] + "/eleicao", json={"id": request.json["id"],
                                                                               "participantes": participantes})
                            break
                        elif len(participantes) == cont:
                            for j in info["servidores_conhecidos"]:
                                if j["id"] == participantes[0]:
                                    requests.post(j["url"] + "/eleicao", json={"id": request.json["id"],
                                                                               "participantes": participantes})
                else:
                    lista = []
                    dados = request.json["id"]
                    print(dados)
                    id = dados.split("-")
                    for i in id[1:]:
                        lista.append(i)
                    print(dados)
                    lista.sort()
                    print(dados)
                    if str(info["identificacao"]) in lista:
                        requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                      json={"coordenador": lista[len(lista) - 1],
                                            "id_eleicao": dados})
                        for i in info["servidores_conhecidos"]:
                            if str(i["id"]) in lista:
                                requests.post(i["url"] + '/eleicao/coordenador',
                                              json={"coordenador": lista[len(lista) - 1],
                                                    "id_eleicao": dados})
                        return jsonify(request.json["id"])
                    else:
                        lista.append(info["identificacao"])
                        lista.sort()
                        for i in lista:
                            cont += 1
                            if i > info["identificacao"]:
                                for j in info["servidores_conhecidos"]:
                                    if j["id"] == i:
                                        requests.post(j["url"] + '/eleicao',
                                                      json={"id": str(dados) + '-' + str(info["identificacao"])})
                                    return jsonify({"id": dados + '-' + str(info["identificacao"])})
                            elif cont == len(lista):
                                for j in info["servidores_conhecidos"]:
                                    if j["id"] == lista[0]:
                                        requests.post(j["url"] + '/eleicao',
                                                      json={"id": str(dados) + '-' + str(info["identificacao"])})
                                    return jsonify({"id": dados + '-' + str(info["identificacao"])})
        except KeyError:
            pass
        except TypeError:
            pass
        return jsonify({"id": auxiliar})
    elif request.method == 'GET':
        time.sleep(1)
        return jsonify({"tipo_de_eleicao_ativa": info["eleicao"], "eleicao_em_andamento": estado})


@app.route('/eleicao/coordenador', methods=['POST', 'GET'])
def coord():
    global dadosCoordenador, dadosEleicao, info, estado
    if request.method == 'GET':
        return jsonify(dadosCoordenador)
    elif request.method == 'POST':
        dados = request.json
        dadosCoordenador["coordenador"] = dados["coordenador"]
        dadosCoordenador["id_eleicao"] = dados["id_eleicao"]
        if int(dadosCoordenador["coordenador"]) == info["identificacao"]:
            info["lider"] = True
        else:
            info["lider"] = False
        time.sleep(2)
        estado = False
        return jsonify(dadosCoordenador)


@app.route('/reset', methods=['GET'])
def reset():
    global dadosCoordenador, info, estado, competicao, lista, auxiliar
    dadosCoordenador["coordenador"] = ""
    dadosCoordenador["id_eleicao"] = ""
    auxiliar = ""
    estado = False
    competicao = True
    info["lider"] = False
    lista = []
    return jsonify(info, dadosCoordenador)


def respFunc():
    global verifica
    time.sleep(10)
    verifica = False


def main():
    port = int(os.environ.get("PORT", 3001))
    app.run(host='0.0.0.0', port=port)


main()
