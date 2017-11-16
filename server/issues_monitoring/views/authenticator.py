from flask import request, jsonify
from .. import app
from ..models import Laboratorio, PreferenciasLaboratorio

@app.route('/authenticator')
def hello():
    return 'Hello'

@app.route('/authenticator/preferencias', methods=['GET'])
def get_preferencias():
    usuario_lab_id = 1 # TODO: Receber através do header Authorization
    
    prefs = PreferenciasLaboratorio.obter(usuario_lab_id)

    return jsonify(prefs)

@app.route('/authenticator/preferencias/<id>', methods=['POST'])
def post_preferencias(id):
    usuario_lab_id = 1 # TODO: Receber através do header Authorization

    data = request.get_json(silent=True)

    if data is None:
        # Não foram enviadas preferências
        return 'Bad Request', 400

    print (repr(data))

    zona_de_conforto = Laboratorio.obter_zona_de_conforto(id)
    
    print (repr(zona_de_conforto))

    if zona_de_conforto is None:
        # O laboratório não existe
        return 'Bad Request', 400

    print('okay')

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
