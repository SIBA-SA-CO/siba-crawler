import pandas as pd
import io

def parseRushPrimeCsv(file_content: bytes) -> pd.DataFrame:
    """
    Parsea el contenido de un archivo CSV proveniente de Rush Prime.

    Intenta decodificar el contenido binario como UTF-8. Si falla por problemas
    de codificación, vuelve a intentar usando cp1252 (Windows Latin-1), lo cual
    es común en archivos CSV generados por aplicaciones en sistemas Windows.

    Args:
        file_content (bytes): Contenido binario del archivo CSV (obtenido como adjunto del correo).

    Returns:
        pd.DataFrame: Un DataFrame de pandas con los datos leídos del CSV.
    """
    try:
        df = pd.read_csv(io.BytesIO(file_content), encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(io.BytesIO(file_content), encoding="cp1252")

    return df
