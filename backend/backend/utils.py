from apps.workers.models import Operador, Worker
from datetime import datetime


def less(x, y):
    return x < y


def swap(data, i, j):
    aux = data[i]
    data[i] = data[j]
    data[j] = aux


def insertion_sort(data):
    [swap(data, j, j - 1) for i in range(0, len(data)) for j in range(i, 0, -1) if not
     less(data[j]['total'], data[j - 1]['total'])]


def getDateByStrig(date):
    date_time_obj = datetime.strptime(date, '%Y-%m-%d - %H:%M:%S')
    return date_time_obj


def getStringByDate(date):
    date_time = date.strftime("%Y-%m-%d - %H:%M:%S")
    return date_time


def getAnualPlanError(year, hotelName, coinName) -> str:
    message = f'Error, el {hotelName} ya tiene un plan de venta anual del año {year} con la moneda {coinName}, pruebe con otro año'
    return message


def getLoginErrorMessage() -> str:
    return 'La contraseña es incorrecta, por favor, inténtelo otra vez'


def getMonthlySalePlanCreateError() -> str:
    return 'Error, ya existe un Plan de Venta mensual con estas credenciales en el hotel actual. Rectifique sus datos'


def getFamilyDeleteError() -> str:
    message = 'No se pueden eliminar ciertas familias porque hay otras entidades q dependen de ella, asegúrese que ningún plan de venta mensual contenga la familia que desea eliminar'
    return message


def getSaleAreaDeleteError() -> str:
    message = 'No se pueden eliminar ciertos Puntos de Ventas porque hay otras entidades q dependen de ella, asegúrese que ningún plan de venta mensual contenga el Punto de Venta que desea eliminar'
    return message


def getAnualPlanDeleteError() -> str:
    return f'Error, no se pueden eliminar ciertos planes de venta anuales porque ya tienen planes de venta mensuales integrados con ellos, si desea eliminar un plan de venta anual asegúrese de eliminar antes los planes de venta mensuales integrados a los mismos'


def getUserNotExistMessage(username) -> str:
    return f'No existe una cuenta con el nombre de usuario ({username}), por favor, inténtelo otra vez'


def getNoAdminDeleteMessage(username) -> str:
    message = f'Lo sentimos. El usuario {username} es el único administrador, no puede dejar el sistema sin ' \
              f'administradores'
    return message


def getUniqueHotelErrorMessage(hotelName) -> str:
    return f'Ya existe un hotel con el nombre "{hotelName}"'


def getDeleteErrorMessage(objectType) -> str:
    return f'No puede eliminar ciertas instancias del {objectType} porque otras entidades dependen de ella'


def getOperatorErrorMessage(idOperator) -> str:
    operator = Operador.objects.get(id_oper=idOperator)
    worker = Worker.objects.get(operador=operator)
    message = 'Ya existe un trabajador con el Operador {}, está ocupado por el trabajador {}'.format(
        operator.descripcion, worker.nombreCompleto())
    return message


def getEvaluatorNotExistError() -> str:
    return 'Error. El trabajador evaluador no está registrado en la Base de Datos del Sistema, debe importar el ' \
           'mismo, es el trabajador que tiene el cargo de Jefe de Departamento ' \
           'de Servicios Gastronómicos '


def getCategoryNoExistError() -> str:
    return 'Ha ocurrido un error al reconstruir la lista de los Cargos de Trabajadores, recuerde que los cargos ' \
           'dependen de las categorías ocupacionales, por favor, asegúrese de tener sincronizadas todas las ' \
           'Categorías Ocupacionales del ZunPr '


def getNoWorkersForEvaluationError() -> str:
    return 'Ha ocurrido un error al construir la lista de las evaluaciones anuales, recuerde que para realizar ' \
           'la evaluación del desempeño debe tener importados desde el ZUNPR los trabajadores del hotel. Impórtelos por favor. ' \



def getNeedCatForWorkerError() -> str:
    return f'Ha ocurrido un error. Asegúrese de que todas las Categorías Ocupacionales estén sincronizadas desde el ZUN'


def getNeedCharForWorkerError() -> str:
    return f'Ha ocurrido un error. Asegúrese de que todas los Cargos Laborales estén sincronizados desde el ZUN'


def getNoPaytimesList() -> str:
    return f'Ha ocurrido un error. Asegúrese de que tener importados los Períodos de Pago desde el ZUN'
