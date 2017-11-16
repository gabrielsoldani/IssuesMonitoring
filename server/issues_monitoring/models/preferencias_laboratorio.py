from . import db

class PreferenciasLaboratorio:
    def __init__(self, usuario_lab_id, lab_id, temperatura_min, temperatura_max, luminosidade_min, luminosidade_max, umidade_min, umidade_max):
        self.usuario_lab_id = usuario_lab_id
        self.lab_id = lab_id
        self.temperatura_min = temperatura_min
        self.temperatura_max = temperatura_max
        self.luminosidade_min = luminosidade_min
        self.luminosidade_max = luminosidade_max
        self.umidade_min = umidade_min
        self.umidade_max = umidade_max

    def obter(usuario_lab_id):
        data = db.fetchall("""
            SELECT
                usuario_lab_id, lab_id, temperatura_min, temperatura_max,
                luminosidade_min, luminosidade_max, umidade_min, umidade_max
            FROM 
                Preferencias_Lab
            WHERE
                usuario_lab_id = ?
        """, (usuario_lab_id,))

        return [PreferenciasLaboratorio(*x) for x in data]

    def salvar(self):
        data = db.execute("""
            INSERT OR REPLACE INTO
                Preferencias_Lab
            (
                usuario_lab_id, lab_id, temperatura_min, temperatura_max,
                luminosidade_min, luminosidade_max, umidade_min, umidade_max
            )
            VALUES
            (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            self.usuario_lab_id, self.lab_id, self.temperatura_min,
            self.temperatura_max, self.luminosidade_min, self.luminosidade_max,
            self.umidade_min, self.umidade_max
        ))
        



