import unidecode
from adm.models import Persona
from django.http import HttpResponse, JsonResponse

def normalizarTexto(texto):
    texto_sin_tildes = unidecode.unidecode(texto)
    return texto_sin_tildes.upper()

def obtenerPersonaCedula(cedula, data):
    try:
        persona = Persona.objects.get(cedula=cedula, status=True)
        data['nombres'] = persona.nombre
        data['nombre'] = persona.nombre
        data['apellido1'] = persona.apellido1
        data['apellido2'] = persona.apellido2
        data['correo'] = persona.correo
        data['celular'] = persona.celular
        data['direccion'] = persona.direccion
        return JsonResponse({'result': True, 'data': data})
    except Exception as ex:
        return JsonResponse({"result": False, 'mensaje': u'Ha ocurrido un error al obtener el formulario.', 'detalle': str(ex)})