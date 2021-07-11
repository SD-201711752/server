import os
import requests
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
verifica = False
competicao = True
estado = False
operacao = 200
lista = []
ID = ""
participantes = []
auxiliar = ""
auxiliar2 = ""

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
    "tipo_de_eleicao_ativa": info["eleicao"],
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
                print(info["eleicao"])
                print(dadosEleicao["tipo_de_eleicao_ativa"])
                info["eleicao"] = dados["eleicao"]
                dadosEleicao["tipo_de_eleicao_ativa"] = dados["eleicao"]
                print(info["eleicao"])
                print(dadosEleicao["tipo_de_eleicao_ativa"])
        except KeyError:
            pass
        return jsonify(info)
    elif request.method == 'GET':
        return jsonify(info)


@app.route('/recurso', methods=['GET', 'POST'])
def funEstado():
    global verifica, operacao, auxiliar2
    if request.method == 'GET':
        if info["lider"] is True:
            return jsonify({"ocupado": True, "id_lider": info["identificacao"]}), operacao
        elif info["lider"] is False:
            if verifica is False:
                return jsonify({"ocupado": verifica, "id_lider": ID}), 409
            elif verifica is True:
                return jsonify({"ocupado": verifica, "id_lider": ID}), 200
    elif request.method == 'POST':
        if info["lider"] is True:
            if verifica is False:
                verifica = True
                operacao = 200
                time.sleep(20)
                verifica = False
            elif verifica is True:
                operacao = 409
            return jsonify({"ocupado": verifica}), operacao
        elif info["lider"] is False:
            operacao = 200
            for servidor in info["servidores_conhecidos"]:
                funcRecurso(servidor["url"])
            if operacao == 200:
                verifica = True
                requests.post(auxiliar2 + '/recurso')
                time.sleep(20)
                verifica = False
            return jsonify({"ocupado": verifica}), operacao


def funcRecurso(url):
    global operacao, auxiliar2, ID
    dados1 = requests.get(url + '/recurso')
    dados2 = dados1.json()
    print(dados1.status_code)
    aux = requests.get(url + '/info').json()
    if dados2["ocupado"] is True and aux["lider"] is not True:
        operacao = 409
    elif aux["lider"] is True:
        auxiliar2 = url
        ID = aux["identificacao"]


def valentao(url):
    global competicao, auxiliar
    dados = requests.get(url + '/info').json()
    try:
        if dados["identificacao"] > info["identificacao"] and dados["status"] == "up" and dados[
            "eleicao"] == "valentao":
            competicao = True
            print(auxiliar)
            requests.post(url + "/eleicao", json={"id": auxiliar})
    except TypeError:
        pass


def anel(url):
    global lista
    try:
        dados = requests.get(url + "/info").json()
        if dados["status"] == "down" or dados["eleicao"] == "valentao":
            pass
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
    global dadosEleicao, competicao, participantes, lista, info
    global auxiliar, estado
    if request.method == 'POST':
        try:
            cont = 0
            competicao = False
            if not estado:
                if type(request.json["id"]) is not int:
                    estado = True
                    print(dadosEleicao["tipo_de_eleicao_ativa"])
                    print(info["eleicao"])
                    print(dadosEleicao["tipo_de_eleicao_ativa"] == "valentao")
                    if dadosEleicao["tipo_de_eleicao_ativa"] == "valentao":
                        auxiliar = request.json["id"]
                        for servidor in info["servidores_conhecidos"]:
                            valentao(servidor["url
                            time.sleep(3)
                        if competicao is False:
                            requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                          json={"coordenador": info["identificacao"],
                                                "id_eleicao": auxiliar})
                            for servidor in info["servidores_conhecidos"]:
                                requests.post(servidor["url"] + '/eleicao/coordenador',
                                              json={"coordenador": info["identificacao"],
                                                    "id_eleicao": auxiliar})
                        print(estado)
                        estado = False
                        print(estado)
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
                        return jsonify({"id":"erro"}), 400
                else:
                    return jsonify({"id": "erro - tipo invalido"}), 400
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
                    aux = list(map(int, lista))
                    aux.sort()
                    if str(info["identificacao"]) in lista:
                        requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                      json={"coordenador": aux[len(lista) - 1],
                                            "id_eleicao": dados})
                        for i in info["servidores_conhecidos"]:
                            if str(i["id"]) in lista:
                                requests.post(i["url"] + '/eleicao/coordenador',
                                              json={"coordenador": aux[len(lista) - 1],
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
        print(estado)
        print(info["eleicao"])
        return jsonify({"tipo_de_eleicao_ativa": info["eleicao"], "eleicao_em_andamento": estado})


@app.route('/eleicao/coordenador', methods=['POST', 'GET'])
def coord():
    global dadosCoordenador, dadosEleicao, info, estado
    if request.method == 'GET':
        return jsonify(dadosCoordenador)
    elif request.method == 'POST':
        dados = request.json
        print(dados["coordenador"])
        print(info["identificacao"])
        dadosCoordenador["coordenador"] = dados["coordenador"]
        dadosCoordenador["id_eleicao"] = dados["id_eleicao"]
        print(dadosCoordenador["coordenador"] == info["identificacao"])
        print(int(dadosCoordenador["coordenador"]) == info["identificacao"])
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


def main():
    port = int(os.environ.get("PORT", 3001))
    app.run(host='0.0.0.0', port=port)


main()
