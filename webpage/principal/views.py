from .Correo import EmailSender
from .DBConnection import DBConnection
from django.shortcuts import render, redirect
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from datetime import timedelta
#import datetime
import json
import re

meses = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

dias_esp={
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miercoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sabado",
    "Sunday": "Domingo",
}

# Función para sumar 15 minutos a una hora dada
def sumar_quince_minutos(hora):
    formato_hora = datetime.strptime(hora, "%H:%M")
    hora_mas_quince = formato_hora + timedelta(minutes=15)
    return hora_mas_quince.strftime("%H%M")

# Función para convertir el mes de texto a número
def obtener_numero_mes(mes):
    meses_dict = {
        "Enero": "01", "Febrero": "02", "Marzo": "03",
        "Abril": "04", "Mayo": "05", "Junio": "06",
        "Julio": "07", "Agosto": "08", "Septiembre": "09",
        "Octubre": "10", "Noviembre": "11", "Diciembre": "12"
    }
    return meses_dict[mes]

def obtener_dias_mes(fecha):
    # Lista para almacenar los días del mes
    dias_mes = []

    # Obtener el último día del mes
    ultimo_dia_mes = (fecha.replace(day=1, month=fecha.month % 12 + 1, year=fecha.year + (fecha.month // 12)) - timedelta(days=1)).day

    # Recorrer todos los días del mes
    for dia in range(1, ultimo_dia_mes + 1):
        fecha_actual = fecha.replace(day=dia)
        # Formatear la fecha en el formato deseado en español
        fecha_formateada = "{} {} de {} del {}".format(
            dias_esp[fecha_actual.strftime("%A")],
            fecha_actual.strftime("%d"),
            meses[fecha_actual.strftime("%B")],
            fecha_actual.strftime("%Y")
        )
        dias_mes.append(fecha_formateada)

    return dias_mes



## CHECK Secretaria
def group_required(group_name, login_url=None):
    def in_group(user):
        for i in group_name:
            if user.groups.filter(name=i).exists():
                return True
        print("pene")
        return False

    return user_passes_test(in_group, login_url=login_url)

def redirect_not_secretaria(view_func):
    decorated_view_func = login_required(group_required(['Secretaria'], login_url='/')(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='Secretaria').exists():
            return redirect('index')
        return decorated_view_func(request, *args, **kwargs)
    return _wrapped_view


## CHECK Cajero
def redirect_not_cajero(view_func):
    decorated_view_func = login_required(group_required(['Cajero'], login_url='/')(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='Cajero').exists():
            return redirect('index')
        return decorated_view_func(request, *args, **kwargs)
    return _wrapped_view

## CHECK Medico
def redirect_not_medico(view_func):
    decorated_view_func = login_required(group_required(['Medico'], login_url='/')(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='Medico').exists():
            return redirect('index')
        return decorated_view_func(request, *args, **kwargs)
    return _wrapped_view

## CHECK Medico y Secretaria
def redirect_not_secretaria_or_medico(view_func):
    groups = ['Medico', 'Secretaria']
    decorated_view_func = login_required(group_required(groups, login_url='/')(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.groups.filter(name='Medico').exists() or request.user.groups.filter(name='Secretaria').exists()):
            return redirect('index')
        return decorated_view_func(request, *args, **kwargs)
    return _wrapped_view



##CONTROL VIEWS
def index(request):
    context = {}
    return render (request,'index.html',context)

def signin(request):
    if request.method == 'GET':
        return render (request,'signin.html')
    else:
        try:
            user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
            if user is None:
                form_context = {
                    'error_form': "Username or password is incorrect."
                }
                return render(request, 'signin.html', form_context)
            login(request, user)
            return redirect('index')
        except:
            form_context = {
                'error_form': "Username or password is incorrect."
            }
            return render(request,'signin.html',form_context)

@login_required
def signout(request):
    logout(request)
    return redirect('index')

##VIEWS SECRETARIA

@redirect_not_secretaria
def admin_horas(request):
    context = {}
    return render (request,'admin_horas.html',context)

@redirect_not_secretaria
def admin_hhcentro(request):
    context = {}
    if request.method == 'POST':
        print("post")
        print(request.POST)
        
        connection = DBConnection()
        
        # Convertir el string a una lista de horas
        horas = json.loads(request.POST['selectedHours'])
        
        # Crear los pares de horas, calculando la segunda hora
        pares_horas_calculados = [(hora.replace(':', ''), sumar_quince_minutos(hora)) for hora in horas]
        
        # Extraer las fechas del diccionario
        fechas = request.POST['selectedDays']

        # Utilizar expresiones regulares para extraer el día y el mes
        patron = r"(\w+) (\d+) de (\w+) del (\d+)"
        matches = re.findall(patron, fechas)
        
        # Generar las fechas en el formato deseado
        fechas_formateadas = []
        for match in matches:
            dia = match[1].zfill(2)
            mes = obtener_numero_mes(match[2])
            año = match[3]
            fecha_formateada = f"{dia}{mes}{año}"
            fechas_formateadas.append(fecha_formateada)

        # Imprimir las fechas formateadas
        for fecha in fechas_formateadas:
            for hora1, hora2 in pares_horas_calculados:
                # Comprobar si ya existe un registro con la misma fecha, horainicio y horafin
                connection.connect()
                query = f"""
                SELECT * FROM hora_atencion
                WHERE fecha = '{fecha}' AND horainicio = {hora1} AND horafin = {hora2};
                """
                runsql = connection.execute_query(query)
                connection.disconnect()

                # Si no hay resultados, insertar el nuevo registro
                if not runsql:
                    connection.connect()
                    query = f"""
                    INSERT INTO hora_atencion (id_horaatencion, fecha, horainicio, horafin)
                    VALUES (nextval('seq_horas_medicas'), '{fecha}', {hora1}, {hora2});
                    """
                    connection.execute_mods(query)
                    connection.disconnect()
                    
                    connection.connect()
                    query = f"""
                    SELECT id_horaatencion
                    FROM hora_atencion
                    WHERE fecha = '{fecha}' AND horainicio = {hora1} AND horafin = {hora2};
                    """
                    idhora = connection.execute_query(query)
                    connection.disconnect()
                    
                    id_horaatencion = idhora[0][0]
                    
                    connection.connect()
                    query = f"""
                    INSERT INTO hora_centromedico (id_hora_centromedico, id_centromedico, id_horaatencion)
                    VALUES (nextval('seq_hora_centromedico'), 1, {id_horaatencion});
                    """
                    connection.execute_mods(query)
                    connection.disconnect()
                else:
                    print(f"Hora Existente: {fecha} horainicio: {hora1}, horafin: {hora2}")
            
        
        return render (request,'admin_horas.html',context)
    elif request.method == 'GET':
        # Obtener la fecha actual
        fecha_actual = datetime.now()

        # Obtener los días del mes actual y del mes siguiente
        dias_mes_actual = obtener_dias_mes(fecha_actual)
        dias_mes_siguiente = obtener_dias_mes(fecha_actual + timedelta(days=30))

        # Combinar las listas de días en una sola lista
        todos_los_dias = dias_mes_actual + dias_mes_siguiente
        context['dias'] = todos_los_dias
        print("get")
        print(request.GET)
        return render (request,'admin_hhcentro.html',context)

@redirect_not_secretaria
def admin_hhmedico(request):
    connection = DBConnection()
    if request.method == 'GET':
        connection.connect()
        fieldsMedico = ['id_medico',
            'nombre_medico']
        query = f"SELECT " + ", ".join(fieldsMedico) + f" FROM medico;"
        runsql = connection.execute_query(query)
        print(runsql)
        connection.disconnect()
        json_data = []
        for row in runsql:
            result = {}
            for i, campo in enumerate(fieldsMedico):
                result[campo] = row[i]
            json_data.append(result)
        print(json_data)
        
        context = {
            'flagInitial': True,
            'medicos': json_data
        }
        return render (request,'admin_hhmedico.html',context)
    elif request.method == 'POST':
        print(request.POST)
        if 'medico' in request.POST:
            
            if 'selectedDays' in request.POST:
                idmedico = request.POST['medico']
                idHorasMedicas = json.loads(request.POST['selectedDays'])
                
                print(type(idHorasMedicas))
                
                for i in idHorasMedicas:
                    connection.connect()
                    query = f"""
                    INSERT INTO medico_disponibilidad (id_med_disp, id_medico, id_hora_centromedico, estado_disponibilidad)
                    VALUES (nextval('seq_medico_disponibilidad'), '{idmedico}', {i}, 'disponible');
                    """
                    connection.execute_mods(query)
                    connection.disconnect()
                
                return redirect('admin_hhmedico')
                
            else:
                idmedico = request.POST['medico']
                fieldsHorasNoAsignadas = [
                    "id_hora_centromedico",
                    "fecha",
                    "horainicio"
                ]
                connection.connect()
                query = f"""select
                        distinct id_hora_centromedico,
                        fecha,
                        horainicio
                        from hora_centromedico
                        inner join hora_atencion using(id_horaatencion)
                        left outer join medico_disponibilidad using (id_hora_centromedico)
                        where id_hora_centromedico not in (select
                        distinct id_hora_centromedico
                        from hora_centromedico
                        inner join hora_atencion using(id_horaatencion)
                        left outer join medico_disponibilidad using (id_hora_centromedico)
                        where id_medico={idmedico})
                        order by 1;"""
                runsql = connection.execute_query(query) 
                connection.disconnect()
                json_data = []
                for row in runsql:
                    result = {}
                    for i, campo in enumerate(fieldsHorasNoAsignadas):
                        result[campo] = row[i]
                    json_data.append(result)
                print(json_data)
                context = {
                    'flagHoras': True,
                    'flagInitial': False,
                    'horas': json_data,
                    'medico': idmedico
                }
                return render (request,'admin_hhmedico.html',context)

@redirect_not_secretaria
def admin_minushhmedico(request):
    connection = DBConnection()
    if request.method == 'GET':
        connection.connect()
        fieldsMedico = ['id_medico',
            'nombre_medico']
        query = f"SELECT " + ", ".join(fieldsMedico) + f" FROM medico;"
        runsql = connection.execute_query(query)
        print(runsql)
        connection.disconnect()
        json_data = []
        for row in runsql:
            result = {}
            for i, campo in enumerate(fieldsMedico):
                result[campo] = row[i]
            json_data.append(result)
        print(json_data)
        
        context = {
            'flagInitial': True,
            'medicos': json_data
        }
        return render (request,'admin_minushhmedico.html',context)
    elif request.method == 'POST':
        print(request.POST)
        if 'medico' in request.POST:
            
            if 'selectedDays' in request.POST:
                idmedico = request.POST['medico']
                idHorasMedicas = json.loads(request.POST['selectedDays'])
                
                print(type(idHorasMedicas))
                
                for i in idHorasMedicas:
                    connection.connect()
                    query = f"""
                    DELETE FROM medico_disponibilidad WHERE id_med_disp = {i};
                    """
                    connection.execute_mods(query)
                    connection.disconnect()
                
                return redirect('admin_minushhmedico')
                
            else:
                idmedico = request.POST['medico']
                fieldsHorasNoAsignadas = [
                    "id_med_disp",
                    "fecha",
                    "horainicio"
                ]
                connection.connect()
                query = f"""select
                            id_med_disp,
                            fecha,
                            horainicio
                            from hora_centromedico
                            inner join hora_atencion using(id_horaatencion)
                            left outer join medico_disponibilidad using (id_hora_centromedico)
                            where id_medico={idmedico} and estado_disponibilidad='disponible'
                            order by 1;"""
                runsql = connection.execute_query(query) 
                connection.disconnect()
                json_data = []
                for row in runsql:
                    result = {}
                    for i, campo in enumerate(fieldsHorasNoAsignadas):
                        result[campo] = row[i]
                    json_data.append(result)
                print(json_data)
                context = {
                    'flagHoras': True,
                    'flagInitial': False,
                    'horas': json_data,
                    'medico': idmedico
                }
                return render (request,'admin_minushhmedico.html',context)

##VIEWS CAJERO

@redirect_not_cajero
def recepcion(request):
    context = {}
    return render (request,'recepcion.html',context)

@redirect_not_cajero
def pago_paciente(request):
    if request.method == 'POST':
        connection = DBConnection()
        print(request.POST)
        
        if 'rutpaciente' in request.POST:
            rutpaciente = request.POST['rutpaciente']
            mailpaciente = request.POST['mailpaciente']
            
            print(rutpaciente)
            print(mailpaciente)
            
            connection.connect()
            
            fieldsHorasMedicas = [
                'id_cita',
                'nombre_paciente',
                'nombre_especialidad',
                'nombre_medico',
                'fecha',
                'horainicio',
                'nombre_centromedico'
                ]
            query = f"SELECT " + ", ".join(fieldsHorasMedicas) + f" FROM view_full_cita where rut_paciente=%s and email_paciente=%s and estado='pendiente';"
            queryargs = (rutpaciente,mailpaciente,)
            runsql = connection.execute_query(query, queryargs)
            print(runsql)
            connection.disconnect()
            json_data = []
            for row in runsql:
                result = {}
                for i, campo in enumerate(fieldsHorasMedicas):
                    result[campo] = row[i]
                json_data.append(result)
            print(json_data)
            context = {
                'horasmedicas': json_data,
                'flagRutPaciente': True,
                'flagInitial': False,
                'flagMailPaciente': False,
            }
            return render (request,'pago_paciente.html',context)
        
        if 'mailpaciente' in request.POST:
            mailpaciente = request.POST['mailpaciente']
            
            context = {
                'flagInitial': False,
                'flagMailPaciente': True,
                'mailpaciente': mailpaciente
                }
            return render (request,'pago_paciente.html',context)
            
    elif request.method == 'GET' and request.GET.get('idCita'):
        idpago = request.GET.get('idCita')
        
        connection = DBConnection()
        connection.connect()
        query = f"UPDATE cita SET estado = 'pagada' WHERE id_cita=%s;"
        queryargs = (idpago,)
        runsql = connection.execute_mods(query, queryargs)
        connection.disconnect()
        context = {
                'flagRutPaciente': False,
                'flagInitial': False,
                'flagMailPaciente': False,
                'flagPagoOK': True
                }
        return render (request,'pago_paciente.html',context)
        
    else:
        context = {
            'flagInitial': True
        }
        return render (request,'pago_paciente.html',context)


## VIEWS LISTA ESPERA Y ATENCION
@redirect_not_secretaria_or_medico
def espera(request):
    if request.method == 'GET':
        connection = DBConnection()
        
        connection.connect()
        fieldsHorasMedicas = [
            'id_cita',
            'nombre_paciente',
            'nombre_especialidad',
            'nombre_medico',
            'fecha',
            'horainicio',
            'nombre_centromedico'
            ]
        query = f"SELECT " + ", ".join(fieldsHorasMedicas) + f" FROM view_full_cita where estado='pagada';"
        runsql = connection.execute_query(query)
        connection.disconnect()
        json_data = []
        if runsql:
            for row in runsql:
                result = {}
                for i, campo in enumerate(fieldsHorasMedicas):
                    result[campo] = row[i]
                json_data.append(result)
            print(json_data)
        context = {
            'horasmedicas': json_data,
        }
        return render (request,'espera.html',context)
    
@redirect_not_medico
def atencion(request):
    if request.method == 'GET' and request.GET.get('idCita'):
        idcita = request.GET.get('idCita')
        
        connection = DBConnection()
        connection.connect()
        query = f"UPDATE cita SET estado = 'ejecutada' WHERE id_cita=%s;"
        queryargs = (idcita,)
        runsql = connection.execute_mods(query, queryargs)
        connection.disconnect()
        
        connection.connect()
        fieldsHorasMedicas = [
            'id_cita',
            'nombre_paciente',
            'nombre_especialidad',
            'nombre_medico',
            'fecha',
            'horainicio',
            'nombre_centromedico'
            ]
        query = f"SELECT " + ", ".join(fieldsHorasMedicas) + f" FROM view_full_cita where id_cita=%s;"
        queryargs = (idcita,)
        runsql = connection.execute_query(query, queryargs)
        print(runsql)
        connection.disconnect()
        json_data = []
        for row in runsql:
            result = {}
            for i, campo in enumerate(fieldsHorasMedicas):
                result[campo] = row[i]
            json_data.append(result)
        print(json_data)
        
        context = {
                'horasmedicas':json_data,
                'flagAtencionOK': True
                }
        return render (request,'atencion.html',context)
        
    else:
        context = {
            'flagInitial': True
        }
        return redirect('espera')

##VIEWS ALL_USERS

def reserva(request):
    print(request.POST)
    idEspecialidad = 0
    idMedico = 0
    idHoraMedico = 0
    nombrePaciente = 0
    
    connection = DBConnection()
    
    if request.method == 'POST':
        if "especialidad" in request.POST:
            idEspecialidad = request.POST['especialidad']
        if "medico" in request.POST:
            idMedico = request.POST['medico']
        if "hora" in request.POST:
            idHoraMedico = request.POST['hora']
        if "nombrepaciente" in request.POST:
            print(request.POST  )
            nombrePaciente = request.POST['nombrepaciente']
            connection.connect()
            query = f"select nextval('seq_id_paciente') from centro_medico LIMIT 1;"
            runsql = connection.execute_query(query)
            connection.disconnect()
            print(runsql[0][0])
            
            idPaciente = runsql[0][0]
            
            nombre_paciente = f"{request.POST['nombrepaciente']} {request.POST['apellido']}"
            email_paciente = f"{request.POST['email']}"
            numtel_paciente = f"{request.POST['numtel']}"
            rut_paciente = f"{request.POST['rutpac']}"
            connection.connect()
            query = f"INSERT INTO paciente (id_paciente, nombre_paciente, email_paciente, numtel_paciente, rut_paciente) VALUES ('{idPaciente}', '{nombre_paciente}', '{email_paciente}', '{numtel_paciente}', '{rut_paciente}');"
            runsql = connection.execute_mods(query)
            connection.disconnect()
            
            connection.connect()
            query = f"select nextval('seq_id_cita') from centro_medico LIMIT 1;"
            runsql = connection.execute_query(query)
            print(runsql)
            connection.disconnect()
            
            idCita = runsql[0][0]
            horaMedica = f"{request.POST['hora']}"
            connection.connect()
            query = f"INSERT INTO cita (id_cita, id_med_disp, id_paciente, estado) VALUES ('{idCita}', '{horaMedica}', '{idPaciente}', 'pendiente');"
            runsql = connection.execute_mods(query)
            connection.disconnect()
            
            
            citaFields= [
                "nombre_paciente",
                "email_paciente",
                "nombre_medico",
                "nombre_especialidad",
                "fecha",
                "horainicio",
                "horafin",
                "nombre_centromedico",
                "direccion_centromedico"
            ]
            connection.connect()
            query = f"select " + ", ".join(citaFields) + f" from view_full_cita where id_cita={idCita};"
            runsql = connection.execute_query(query)
            connection.disconnect()
            
            print(type(runsql[0][4]))
            
            context = {
                'flagPaciente': True
            }
            
            for i, campo in enumerate(citaFields):
                context[campo] = runsql[0][i]
            
            preFechaCita = context["fecha"]
            fechaCita = datetime.strptime(preFechaCita, "%d%m%Y").strftime("%d de %B del %Y")
            fechaCita = fechaCita.replace(datetime.strptime(preFechaCita, "%d%m%Y").strftime('%B'), meses[datetime.strptime(preFechaCita, "%d%m%Y").strftime('%B')])
            context["fecha"] = fechaCita
            
            print(context["fecha"])
            
            emailsender = EmailSender()
            subject = "Hora confirmada exitosamente"
            body = f"Estimad@ {context['nombre_paciente']}\n\nSe ha confirmado su hora para la especialidad {context['nombre_especialidad']} con el(la) profesional {context['nombre_medico']}.\nLa cita esta agendada para el dia {context['fecha']} a las {context['horainicio']}.\nDebe concurrir al centro médico {context['nombre_centromedico']} ubicado en {context['direccion_centromedico']}.\n\nSaludos cordiales,\nCentro medico Galenos."
            
            email_enviado = emailsender.send_email(email_paciente, subject, body)
            if email_enviado:
                print("Correo enviado exitosamente.")
            else:
                print("Error al enviar el correo.")
            
            
            return render (request,'reserva.html',context)
    
    
    if idEspecialidad != 0:
        if idMedico != 0:
            if idHoraMedico != 0:
                if nombrePaciente != 0:
                    connection.connect()
                    query = f"select max(id_paciente) from paciente;"
                    runsql = connection.execute_query(query)
                    print(runsql)
                else:
                    connection.connect()
                    query = f"UPDATE medico_disponibilidad SET estado_disponibilidad = 'nodisponible' WHERE id_med_disp = {idHoraMedico};"
                    runsql = connection.execute_mods(query)
                    connection.disconnect()
                    context = {
                        'flagEspecialidad': False,
                        'flagMedico': False,
                        'flagHora': True,
                        'idHoraSel': idHoraMedico,
                    }
                    return render (request,'reserva.html',context)
            else:
                connection.connect()
                fieldsHora = ['id_med_disp',
                    'fecha',
                    'horainicio',
                    'horafin']
                query = f"SELECT " + ", ".join(fieldsHora) + f" from medico_disponibilidad inner join hora_centromedico using(id_hora_centromedico) inner join hora_atencion using(id_horaatencion) where id_medico={idMedico} and estado_disponibilidad='disponible';"
                runsql = connection.execute_query(query)
                print(runsql)
                connection.disconnect()
                json_data = []
                for row in runsql:
                    result = {}
                    for i, campo in enumerate(fieldsHora):
                        if campo in ['horainicio', 'horafin']:
                            hora_original = str(row[i])
                            # Formatear la hora de '1045' a '10:45'
                            hora_formateada = f'{hora_original[:2]}:{hora_original[2:]}'
                            result[campo] = hora_formateada
                        elif campo == 'fecha':
                            fecha_original = str(row[i])
                            # Formatear la fecha de '30102023' a '30-10-2023'
                            fecha_formateada = f'{fecha_original[:2]}-{fecha_original[2:4]}-{fecha_original[4:]}'
                            result[campo] = fecha_formateada
                        else:
                            result[campo] = row[i]
                    json_data.append(result)
                print(json_data)
                context = {
                    'flagEspecialidad': False,
                    'flagMedico': True,
                    'idMedicoSel': idMedico,
                    'idEspecilidadSel': idEspecialidad,
                    'horas': json_data
                }
                return render (request,'reserva.html',context)
        else:
            connection.connect()
            fieldsMedico = ['id_medico',
                'nombre_medico']
            query = f"SELECT " + ", ".join(fieldsMedico) + f" FROM medico where id_especialidad={idEspecialidad};"
            runsql = connection.execute_query(query)
            print(runsql)
            connection.disconnect()
            json_data = []
            for row in runsql:
                result = {}
                for i, campo in enumerate(fieldsMedico):
                    result[campo] = row[i]
                json_data.append(result)
            print(json_data)
            context = {
                'flagEspecialidad': True,
                'idEspecilidadSel': idEspecialidad,
                'medicos': json_data
            }
            return render (request,'reserva.html',context)
        
    else:
        connection.connect()
        fieldsEspecialidad = ['id_especialidad',
            'nombre_especialidad']
        query = f"SELECT " + ", ".join(fieldsEspecialidad) + f" FROM especialidad;"
        runsql = connection.execute_query(query)
        print(runsql)
        connection.disconnect()
        json_data = []
        for row in runsql:
            result = {}
            for i, campo in enumerate(fieldsEspecialidad):
                result[campo] = row[i]
            json_data.append(result)
        print(json_data)
        context = {
            'especialidades': json_data
        }
        return render (request,'reserva.html',context)

def anulacion(request):
    if request.method == 'POST':
        connection = DBConnection()
        print(request.POST)
        
        if 'rutpaciente' in request.POST:
            rutpaciente = request.POST['rutpaciente']
            mailpaciente = request.POST['mailpaciente']
            
            print(rutpaciente)
            print(mailpaciente)
            
            connection.connect()
            
            fieldsHorasMedicas = [
                'id_cita',
                'nombre_paciente',
                'nombre_especialidad',
                'nombre_medico',
                'fecha',
                'horainicio',
                'nombre_centromedico'
                ]
            query = f"SELECT " + ", ".join(fieldsHorasMedicas) + f" FROM view_full_cita where rut_paciente=%s and email_paciente=%s and estado='pendiente';"
            queryargs = (rutpaciente,mailpaciente,)
            runsql = connection.execute_query(query, queryargs)
            print(runsql)
            connection.disconnect()
            json_data = []
            for row in runsql:
                result = {}
                for i, campo in enumerate(fieldsHorasMedicas):
                    result[campo] = row[i]
                json_data.append(result)
            print(json_data)
            context = {
                'horasmedicas': json_data,
                'flagRutPaciente': True,
                'flagInitial': False,
                'flagMailPaciente': False,
            }
            return render (request,'anulacion.html',context)
        
        if 'mailpaciente' in request.POST:
            mailpaciente = request.POST['mailpaciente']
            
            context = {
                'flagInitial': False,
                'flagMailPaciente': True,
                'mailpaciente': mailpaciente
                }
            return render (request,'anulacion.html',context)
            
    elif request.method == 'GET' and request.GET.get('idCita'):
        idanulacion = request.GET.get('idCita')
        
        connection = DBConnection()
        connection.connect()
        query = f"UPDATE cita SET estado = 'anulada' WHERE id_cita=%s;"
        queryargs = (idanulacion,)
        runsql = connection.execute_mods(query, queryargs)
        connection.disconnect()
        context = {
                'flagRutPaciente': False,
                'flagInitial': False,
                'flagMailPaciente': False,
                'flagAnulacionOK': True
                }
        return render (request,'anulacion.html',context)
        
    else:
        context = {
            'flagInitial': True
        }
        return render (request,'anulacion.html',context)


