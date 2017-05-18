# -*- coding: utf-8 -*-
"""
Created on Wed May 17 00:20:42 2017

@author: Brian Confessor e Débora Pina
"""

from ..common.mail import send_email
from ..models import  AdministradorSistema
from . import db

#checks if lights were left on while no one was in lab
def CheckForForgottenLights():
    #checks for people in lab
    data = db.fetchall("""SELECT User_Lab.email 
                          FROM User_Lab, Presenca WHERE User_Lab.user_id=Presenca.user_id AND Presenca.presente=1;""")
    presentUsers =[]
    for row in data:
        presentUsers.append(str(row[0]))
    
    if(len(presentUsers)==0):
        #no one is in the lab, checks if lights are on
        data = db.fetchall("""SELECT lum 
                              FROM Log_Lab ORDER BY data DESC LIMIT 1;""")
        lightsOn=False
        for row in data:
            lightsOn=row[0]
            
        if(lightsOn):
            #lights are on, send email to supervisor
            subject = "Aviso de luz acesa"
            msgContent = """
Caro responsável,
Você está recebendo essa mensagem pois a luz do laboratorio foi deixada acesa e não há mais funcionários presentes.
Pedimos que procure uma solução quanto a isso, para evitar o gasto desnecessário de energia.
\n\nAtenciosamente, \nEquipe ISSUES Monitoring"""
    
            admins = AdministradorSistema.obter_administradores()
            emails = [a.email for a in admins]
            #if it got here, just send message to supervisor(s)
            send_email(subject, msgContent, emails)


def CheckForEnvironmentConditions():
    data = db.fetchall("""
        SELECT temp_min, temp_max, umid_min, umid_max 
        FROM Zona_de_Conforto_Lab;""")
    umid_min=0
    umid_max=0
    temp_min=0
    temp_max=0

    for row in data:
        temp_min=row[0]
        temp_max=row[1]
        umid_min=row[2]
        umid_max=row[3]

    current_temp = 0
    current_umid = 0
    data = db.fetchall("""SELECT temp, umid 
                          FROM Log_Lab ORDER BY data DESC LIMIT 1;""")
    
    for row in data:
        current_temp = row[0]
        current_umid = row[1]
    
    if (current_temp < temp_min or current_temp > temp_max):
        subject = "Aviso de temperatura anormal"
        msgContent = """
Caro responsável,
Você está recebendo essa mensagem pois a temperatura do laboratorio se encontra fora da zona de conforto.
Pedimos que procure uma solução quanto a isso.
\n\nAtenciosamente, \nEquipe ISSUES Monitoring"""

        data = db.fetchall("""
            SELECT u.email
            FROM Presenca p
            INNER JOIN User_Lab u
              ON p.user_id = u.user_id
            WHERE presente = 1;""")

        admins = AdministradorSistema.obter_administradores()
        emails = [a.email for a in admins]
        if len(data) != 0:
            for d in data:
                emails += [d[0]]    

        #if it got here, just send message to supervisor(s)
        send_email(subject, msgContent, emails)
        
    if (current_umid < umid_min or current_umid > umid_max):
        subject = "Aviso de umidade anormal"
        msgContent = """
Caro responsável,
Você está recebendo essa mensagem pois a umidade do laboratorio se encontra fora da zona de conforto.
Pedimos que procure uma solução quanto a isso.
\n\nAtenciosamente, \nEquipe ISSUES Monitoring"""

        admins = AdministradorSistema.obter_administradores()
        emails = [a.email for a in admins]

        #if it got here, just send message to supervisor(s)
        send_email(subject, msgContent, emails)     