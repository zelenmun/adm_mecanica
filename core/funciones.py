import unidecode

def normalizarTexto(texto):
    texto_sin_tildes = unidecode.unidecode(texto)
    return texto_sin_tildes.upper()