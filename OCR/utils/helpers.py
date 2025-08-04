import re

def limpiar_texto_ocr(texto: str) -> str:
    texto = re.sub(r"[^\w\sÁÉÍÓÚáéíóúÑñ@.:\-_\/]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"(TEXT|DATE|UUID|BOOLEAN|DECIMAL|INT|TIMESTAMP)", r"\1\n", texto)
    basura = ["wip", "wp", "wD", "uwID", "ide", "ido", "hi", "eo", "dlientede", "dlienteid", "uwID", "CU", "LY"]
    for palabra in basura:
        texto = re.sub(rf"\b{palabra}\b", "", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\n\s*\n", "\n", texto)
    return texto.strip()
