from flask import request, jsonify
from .. import app, controllers
from ..models import Laboratorio, PreferenciasLaboratorio, UsuarioLab, Evento
from datetime import datetime

def autenticar():
    auth = request.authorization

    if not auth:
        return None

    try:
        usuario_mydenox_id = int(auth.username)
    except ValueError:
        return None

    usuario = controllers.obter_usuario_lab(usuario_mydenox_id)
    if usuario is None:
        return None

    usuario_lab_id = usuario.id

    # Não autorizar usuários que não tenham token definido (legado).
    if usuario.token is None:
        return None

    if usuario.token != auth.password:
        return None

    return usuario_mydenox_id, usuario_lab_id 

@app.route('/authenticator')
def hello():
    return 'Hello'

@app.route('/authenticator/entrada/<id>', methods=['POST'])
def post_entrada(id):
    autenticacao = autenticar()
    if autenticacao is None:
        return 'Unauthorized', 401
    usuario_mydenox_id, usuario_lab_id = autenticacao

    # TO DO: Checar se o usuário tem permissão para entrar no laboratório
    
    if Laboratorio.obter(id) is None:
        return 'Unauthorized', 401

    if UsuarioLab.presente(usuario_mydenox_id, id):
        # O usuário já está presente no laboratório.
        return '', 204

    now = int(datetime.now().timestamp())

    eventos = [Evento(now, 'IN', usuario_mydenox_id, id)]

    UsuarioLab.registrar_presenca(eventos)

    return '', 204

@app.route('/authenticator/saida/<id>', methods=['POST'])
def post_saida(id):
    autenticacao = autenticar()
    if autenticacao is None:
        return 'Unauthorized', 401
    usuario_mydenox_id, usuario_lab_id = autenticacao

    # TO DO: Checar se o usuário tem permissão para entrar no laboratório

    if Laboratorio.obter(id) is None:
        return 'Unauthorized', 401
    
    if not UsuarioLab.presente(usuario_mydenox_id, id):
        # O usuário não está presente no laboratório.
        return '', 204

    now = int(datetime.now().timestamp())

    eventos = [Evento(now, 'OUT', usuario_mydenox_id, id)]

    UsuarioLab.registrar_presenca(eventos)

    return '', 204

@app.route('/authenticator/laboratorios', methods=['GET'])
def get_laboratorios():
    autenticacao = autenticar()
    if autenticacao is None:
        return 'Unauthorized', 401
    usuario_mydenox_id, usuario_lab_id = autenticacao

    labs = Laboratorio.obter_laboratorios_autorizados(usuario_mydenox_id)

    response = []
    for lab_id, lab_nome, lab_wifi in labs:
        response.append({
            'id': lab_id,
            'nome': lab_nome,
            'wifi': lab_wifi
        })

    return jsonify(response)

@app.route('/authenticator/preferencias', methods=['GET'])
def get_preferencias():
    autenticacao = autenticar()
    if autenticacao is None:
        return 'Unauthorized', 401
    usuario_mydenox_id, usuario_lab_id = autenticacao
    
    prefs = PreferenciasLaboratorio.obter(usuario_lab_id)

    response = []
    for x in prefs:
        lab = Laboratorio.obter(x.lab_id)
        
        if lab is None:
            # O laboratório foi removido
            continue

        response.append({
            'id_laboratorio': x.lab_id,
            'nome_laboratorio': lab.nome,
            'temperatura_min': x.temperatura_min,
            'temperatura_max': x.temperatura_max,
            'luminosidade_min': x.luminosidade_min,
            'luminosidade_max': x.luminosidade_max,
            'umidade_min': x.umidade_min,
            'umidade_max': x.umidade_max
        })

    return jsonify(response)

@app.route('/authenticator/preferencias/<id>', methods=['POST'])
def post_preferencias(id):
    print('hey')
    autenticacao = autenticar()
    if autenticacao is None:
        return 'Unauthorized', 401
    usuario_mydenox_id, usuario_lab_id = autenticacao

    data = request.get_json(silent=True)

    if data is None:
        # Não foram enviadas preferências
        return 'Bad Request', 400

    zona_de_conforto = Laboratorio.obter_zona_de_conforto(id)

    if zona_de_conforto is None:
        # O laboratório não existe
        return 'Bad Request', 400

    if (('temperatura_min' in data and data['temperatura_min'] < zona_de_conforto['temperatura_min']) or
        ('temperatura_max' in data and data['temperatura_max'] > zona_de_conforto['temperatura_max']) or
        #('luminosidade_min' in data and data['luminosidade_min'] < zona_de_conforto['luminosidade_min']) or
        #('luminosidade_max' in data and data['luminosidade_max'] > zona_de_conforto['luminosidade_max']) or
        ('umidade_min' in data and data['umidade_min'] < zona_de_conforto['umidade_min']) or
        ('umidade_max' in data and data['umidade_max'] > zona_de_conforto['umidade_max'])):
        return jsonify(zona_de_conforto), 403

    preferencias = PreferenciasLaboratorio(
        usuario_lab_id = usuario_lab_id,
        lab_id = id,
        temperatura_min = data.get('temperatura_min'),
        temperatura_max = data.get('temperatura_max'),
        luminosidade_min = data.get('luminosidade_min'),
        luminosidade_max = data.get('luminosidade_max'),
        umidade_min = data.get('umidade_min'),
        umidade_max = data.get('umidade_max')
    )
    preferencias.salvar()

    return '', 204

@app.route('/authenticator/notificacoes', methods=['GET'])
@app.route('/authenticator/notificacoes/<int:data>', methods=['GET'])
def get_notificacoes(data = -1):
    autenticacao = autenticar()
    if autenticacao is None:
        return 'Unauthorized', 401
    usuario_mydenox_id, usuario_lab_id = autenticacao

    notificacoes = []

    labs = Laboratorio.obter_laboratorios_autorizados(usuario_mydenox_id)

    for lab_id, lab_nome, _ in labs:
        prefs = PreferenciasLaboratorio.obter_do_laboratorio(usuario_lab_id, lab_id)

        if prefs is None:
            continue

        now = int(datetime.now().timestamp())
        _, temperatura, umidade, luminosidade = Laboratorio.obter_ultima_medida(lab_id, data, now)

        if temperatura is not None:
            if prefs.temperatura_min is not None and temperatura < prefs.temperatura_min:
                notificacoes.append({
                    'titulo': 'Alerta de temperatura',
                    'mensagem': 'A temperatura de {} ({:.0f}°C) está abaixo das suas preferências ({:d}°C).'.format(lab_nome, temperatura, prefs.temperatura_min)
                })

            if prefs.temperatura_max is not None and temperatura > prefs.temperatura_max:
                notificacoes.append({
                    'titulo': 'Alerta de temperatura',
                    'mensagem': 'A temperatura de {} ({:.0f}°C) está acima das suas preferências ({:d}°C).'.format(lab_nome, temperatura, prefs.temperatura_max)
                })
        
        if umidade is not None:
            if prefs.umidade_min is not None and umidade < prefs.umidade_min:
                notificacoes.append({
                    'titulo': 'Alerta de umidade',
                    'mensagem': 'A umidade de {} ({:.0f}%) está abaixo das suas preferências ({:d}%).'.format(lab_nome, umidade, prefs.umidade_min)
                })

            if prefs.umidade_max is not None and umidade > prefs.umidade_max:
                notificacoes.append({
                    'titulo': 'Alerta de umidade',
                    'mensagem': 'A umidade de {} ({:.0f}%) está acima das suas preferências ({:d}%).'.format(lab_nome, umidade, prefs.umidade_max)
                })
        
        # TO DO: Luminosidade

    return jsonify(notificacoes)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response
