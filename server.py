import os
import requests
import threading
import time

from flask import Flask, jsonify, request

app = Flask(__name__)
ServidoresValidos = []
eleicao = "valentao"
participantes = []
competicao = True
verifica = False
auxiliar2 = ""
operacao = 200
estado = False
auxiliar = ""
marcador = 0
lista = []
ID = ""

info = {
    "componente": "server",
    "versao": "0.1",
    "descricao": "serve os clientes com os servicos disponilizados",
    "ponto_de_acesso": "https://sd-dmss.herokuapp.com",
    "status": "up",
    "identificacao": 7,
    "lider": 0,
    "eleicao": eleicao,
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
    "tipo_de_eleicao_ativa": eleicao,
    "eleicao_em_andamento": estado
}


@app.route('/info', methods=['GET', 'POST'])
def funInfo():
    global info, dadosEleicao, eleicao
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
            if dados["lider"] in [0, 1]:
                info["lider"] = dados["lider"]
        except KeyError:
            pass
        try:
            if dados["eleicao"] == "valentao" or dados["eleicao"] == "anel":
                eleicao = dados["eleicao"]
                info["eleicao"] = dados["eleicao"]
                dadosEleicao["tipo_de_eleicao_ativa"] = dados["eleicao"]
        except KeyError:
            pass
        return jsonify(info)
    elif request.method == 'GET':
        return jsonify(info)


@app.route('/recurso', methods=['GET', 'POST'])
def funEstado():
    global verifica, operacao, auxiliar2, marcador
    if request.method == 'GET':
        if info["lider"] == 1:
            if verifica is False:
                return jsonify({"ocupado": verifica, "id_lider": info["identificacao"]}), 200
            elif verifica is True:
                return jsonify({"ocupado": verifica, "id_lider": info["identificacao"]}), 409
        elif info["lider"] == 0 and checkLider() is True:
            if verifica is False:
                return jsonify({"ocupado": verifica, "id_lider": ID}), 200
            elif verifica is True:
                return jsonify({"ocupado": verifica, "id_lider": ID}), 409
        else:
            return jsonify({"erro": "não existe lider"}), 400
    elif request.method == 'POST':
        if info["lider"] == 1:
            if verifica is False:
                verifica = True
                threading.Thread(target=respFunc, args=()).start()
                operacao = 200
            elif verifica is True:
                operacao = 409
            return jsonify({"ocupado": verifica, "id_lider": info["identificacao"]}), operacao
        elif info["lider"] == 0 and checkLider() is True:
            for servidor in info["servidores_conhecidos"]:
                funcRecurso(servidor["url"])
            if operacao == 200 and marcador == 0:
                verifica = True
                marcador = 1
                requests.post(auxiliar2 + '/recurso')
                threading.Thread(target=respFunc, args=()).start()
            elif marcador == 1:
                operacao = 409
            return jsonify({"ocupado": verifica, "id_lider": ID}), operacao
        else:
            return jsonify({"erro": "não existe lider"}), 400


def funcRecurso(url):
    global operacao, auxiliar2, ID
    try:
        dados1 = requests.get(url + '/recurso')
        dados2 = dados1.json()
        aux = requests.get(url + '/info').json()
        if dados2["ocupado"] is True and aux["lider"] == 0:
            operacao = 409
        elif aux["lider"] == 1:
            auxiliar2 = url
            ID = aux["identificacao"]
    except requests.ConnectionError:
        pass
    except KeyError:
        pass
    except TypeError:
        pass


def checkLider():
    global ID
    cont = 0
    for servidor in info["servidores_conhecidos"]:
        dados = requests.get(servidor["url"] + '/info').json()
        if dados["lider"] == 1:
            cont = 1
            ID = dados["identificacao"]
            break
    if cont == 1:
        return True
    else:
        return False


def respFunc():
    global verifica, operacao, marcador
    time.sleep(20)
    marcador = 0
    operacao = 200
    verifica = False


def valentao(url):
    global competicao, auxiliar, info, ServidoresValidos
    dados = requests.get(url + '/info').json()
    print(info["identificacao"])
    try:
        if dados["identificacao"] > info["identificacao"] and dados["status"] == "up" and dados[
            "eleicao"] == "valentao":
            competicao = True
            requests.post(url + '/eleicao', json={"id": auxiliar})
        if dados["status"] == "up" and dados["eleicao"] == "valentao":
            ServidoresValidos.append(url)
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
            return
    except requests.ConnectionError:
        pass
    except KeyError:
        pass
    except TypeError:
        pass


@app.route('/eleicao', methods=['GET', 'POST'])
def funEleicao():
    global dadosEleicao, competicao, participantes, lista, info, ServidoresValidos
    global auxiliar, estado, eleicao
    if request.method == 'POST':
        try:
            cont = 0
            competicao = False
            auxiliar = request.json["id"]
            if not estado:
                if type(auxiliar) is not int:
                    estado = True
                    if eleicao == "valentao":
                        ServidoresValidos = []
                        for servidor in info["servidores_conhecidos"]:
                            valentao(servidor["url"])
                            time.sleep(2)
                        if competicao is False:
                            requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                          json={"coordenador": info["identificacao"],
                                                "id_eleicao": auxiliar})
                            for servidor in ServidoresValidos:
                                requests.post(servidor + '/eleicao/coordenador',
                                              json={"coordenador": info["identificacao"],
                                                    "id_eleicao": auxiliar})
                        estado = False
                    elif dadosEleicao["tipo_de_eleicao_ativa"] == "anel":
                        lista = []
                        for servidor in info["servidores_conhecidos"]:
                            anel(servidor["url"])
                        ServidoresValidos = []
                        lista.append((info["ponto_de_acesso"], info["identificacao"]))
                        listaServidores = sorted(lista, key=lambda x: x[1])
                        for servidor in listaServidores:
                            cont += 1
                            if servidor[1] > info["identificacao"]:
                                requests.post(servidor[0] + '/eleicao', json={"id": auxiliar + '-'
                                                                                    + str(info["identificacao"])})
                                return jsonify({"id": auxiliar})
                            elif len(listaServidores) == cont:
                                requests.post(listaServidores[0][0] + '/eleicao', json={"id": auxiliar + '-'
                                                                                              + str(
                                    info["identificacao"])})
                                return jsonify({"id": auxiliar})
                    else:
                        return jsonify({"id": "erro"}), 400
                else:
                    return jsonify({"id": "erro - tipo invalido"}), 400
            elif info["eleicao"] == "anel" and estado is True:
                validacao = []
                dados = request.json["id"]
                id = dados.split("-")
                for i in id[1:]:
                    validacao.append(i)
                aux = list(map(int, validacao))
                aux.sort()
                if str(info["identificacao"]) in validacao:
                    requests.post(info["ponto_de_acesso"] + '/eleicao/coordenador',
                                  json={"coordenador": aux[len(validacao) - 1],
                                        "id_eleicao": dados})
                    for i in lista:
                        requests.post(i[0] + '/eleicao/coordenador',
                                      json={"coordenador": aux[len(lista) - 1],
                                            "id_eleicao": dados})
                    return jsonify(dados)
                else:
                    validacao.append(info["identificacao"])
                    validacao.sort()
                    for i in validacao:
                        cont += 1
                        if i > info["identificacao"]:
                            for j in lista:
                                if j[1] == i:
                                    requests.post(j[0] + '/eleicao',
                                                  json={"id": str(dados) + '-' + str(info["identificacao"])})
                                return jsonify({"id": dados + '-' + str(info["identificacao"])})
                        elif cont == len(lista):
                            for j in lista:
                                if j[1] == validacao[0]:
                                    requests.post(j[0] + '/eleicao',
                                                  json={"id": str(dados) + '-' + str(info["identificacao"])})
                                return jsonify({"id": dados + '-' + str(info["identificacao"])})
        except KeyError:
            pass
        except TypeError:
            pass
        return jsonify({"id": auxiliar})
    elif request.method == 'GET':
        return jsonify({"tipo_de_eleicao_ativa": eleicao, "eleicao_em_andamento": estado})


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
            info["lider"] = 1
        else:
            info["lider"] = 0
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
    info["lider"] = 0
    lista = []
    return jsonify(info, dadosCoordenador)


def main():
    port = int(os.environ.get("PORT", 3001))
    app.run(host='0.0.0.0', port=port)


main()
