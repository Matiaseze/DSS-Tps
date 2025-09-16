import pandas as pd
import numpy as np
import re

def leer_y_mostrar_columnas(df,num_cols):
    """
    Lee un DataFrame y muestra sus columnas.
    
    Parámetros:
    df (pd.DataFrame, columnas): El DataFrame a analizar.
    
    Retorna:
    list: Una lista con los nombres de las columnas del DataFrame.
    """
    df = pd.read_csv('fifa21.csv')

    print(df.head(num_cols))

    return df.columns.tolist()

def quitar_columnas_innecesarias(df, columnas_a_quitar):
    """
    Quita columnas innecesarias de un DataFrame.
    
    Parámetros:
    df (pd.DataFrame): El DataFrame del cual se eliminarán las columnas.
    columnas_a_quitar (list): Una lista con los nombres de las columnas a eliminar.
    
    Retorna:
    pd.DataFrame: El DataFrame sin las columnas especificadas.
    """

    df = df.drop(columns=columnas_a_quitar)
    return df

def revisar_formatos(df, columnas):
    """
    Revisa los formatos de valores en columnas específicas de un DataFrame.
    
    Para columnas numéricas detecta:
        - Terminados en 'M'
        - Terminados en 'K'
        - Terminados en 'kg'
        - Terminados en 'lbs'
        - Decimales
        - Vacíos / espacios en blanco
        - Nulos
    
    Para la columna 'Club' detecta:
        - Espacios al comienzo
        - Contiene números
        - Solo espacios en blanco
        - Nulos
    
    Retorna:
    dict: Diccionario con resumen de conteos por formato en cada columna.
    """
    resultados = {}

    for col in columnas:
        conteos = {}

        # contabilizar nulos directamente con pandas
        conteos["nulos"] = df[col].isna().sum()

        if col.lower() == "club":
            conteos.update({
                "espacios al comienzo": 0,
                "contiene numeros": 0,
            })

            for val in df[col].dropna().astype(str):
                if val.startswith(" "):  # espacio al comienzo
                    conteos["espacios al comienzo"] += 1
                if re.search(r"\d", val):  # contiene número
                    conteos["contiene numeros"] += 1

        else:
            conteos.update({
                "terminados en m": 0,
                "terminados en k": 0,
                "terminados en kg": 0,
                "terminados en lbs": 0,
                "decimales": 0
            })

            for val in df[col].dropna().astype(str):
                v = val.strip().lower()

                if v.endswith("m"):
                    conteos["terminados en m"] += 1
                elif v.endswith("k"):
                    conteos["terminados en k"] += 1
                elif v.endswith("kg"):
                    conteos["terminados en kg"] += 1
                elif v.endswith("lbs"):
                    conteos["terminados en lbs"] += 1
                elif re.match(r"^\d+\.\d+$", v):  # número decimal
                    conteos["decimales"] += 1

        resultados[col] = conteos

        # salida legible
        print(f"\n--- {col} ---")
        for k, v in conteos.items():
            if v > 0:
                print(f"{k}: {v}")

    return resultados

def limpiar_columna_club(df, columna='Club'):
    """
    Limpia la columna Club eliminando caracteres raros, números al comienzo y espacios extra.
    Deja solo el nombre del club.
    
    Parámetros:
    df (pd.DataFrame): DataFrame con la columna Club.
    columna (str): Nombre de la columna a limpiar (por defecto 'Club').
    
    Retorna:
    pd.DataFrame: DataFrame con la columna Club limpia.
    """
    import re
    def limpiar_club(club):
        if pd.isna(club):
            return None
        club = str(club).strip()
        club = re.sub(r'^[^a-zA-Z]+', '', club)  # elimina caracteres no alfabéticos al inicio
        club = club.strip()
        return club
    df[columna] = df[columna].astype(str).apply(limpiar_club)
    return df


def limpiar_columna_hits(df, columna='Hits'):
    """
    Limpia la columna Hits convirtiendo a entero:
    - Ignora vacíos y guiones (-), devolviendo np.nan.
    - Convierte valores con 'K' a miles.
    - Convierte decimales y enteros a int.
    - Si no puede convertir, deja np.nan.
    
    Parámetros:
    df (pd.DataFrame): DataFrame con la columna Hits.
    columna (str): Nombre de la columna a limpiar (por defecto 'Hits').
    
    Retorna:
    pd.DataFrame: DataFrame con la columna Hits limpia.
    """
    def hits_to_int(x):
        if pd.isna(x) or x == '-':
            return np.nan
        x = str(x).strip().replace(',', '')
        if x.endswith('K'):
            try:
                return int(float(x[:-1]) * 1000)
            except:
                return np.nan
        try:
            return int(float(x))
        except:
            return np.nan
        
    df[columna] = df[columna].apply(hits_to_int)
    return df

def limpiar_columna_weight(df, columna='Weight', nueva_columna='Weight_kg'):
    """
    Limpia la columna Weight convirtiendo valores en kg o lbs a kilogramos enteros.
    - Convierte ambos formatos a kilogramos y los deja como enteros.
    - Si no puede convertir, deja None.
    
    Parámetros:
    df (pd.DataFrame): DataFrame con la columna Weight.
    columna (str): Nombre de la columna a limpiar (por defecto 'Weight').
    nueva_columna (str): Nombre de la nueva columna (por defecto 'Weight_kg').
    
    Retorna:
    pd.DataFrame: DataFrame con la nueva columna en kg y sin la columna original.
    """
    def weight_to_kg(w):
        if pd.isna(w):
            return None
        w = str(w).strip().lower()
        if w.endswith('kg'):
            try:
                return int(float(w.replace('kg', '').strip()))
            except:
                return None
        if w.endswith('lbs'):
            try:
                lbs = float(w.replace('lbs', '').strip())
                return int(round(lbs * 0.453592))
            except:
                return None
        try:
            return int(float(w))
        except:
            return None
    df[nueva_columna] = df[columna].apply(weight_to_kg)
    df = df.drop(columns=[columna])
    return df

def limpiar_columna_height(df, columna='Height', nueva_columna='Height_cm'):
    """
    Limpia la columna Height convirtiendo valores en formato 'cm' o pies/pulgadas a centímetros.
    - Si el valor está en 'cm', lo convierte a float.
    - Si el valor está en formato pies y pulgadas (ej: 5'11"), lo convierte a cm.
    - Si no puede convertir, deja None.
    
    Parámetros:
    df (pd.DataFrame): DataFrame con la columna Height.
    columna (str): Nombre de la columna a limpiar (por defecto 'Height').
    nueva_columna (str): Nombre de la nueva columna (por defecto 'Height_cm').
    
    Retorna:
    pd.DataFrame: DataFrame con la nueva columna en cm y sin la columna original.
    """
    def height_to_cm(h):
        if isinstance(h, str):
            if 'cm' in h:
                try:
                    return float(h.replace('cm', '').strip())
                except:
                    return None
            elif "'" in h:
                try:
                    parts = h.replace('"', '').split("'")
                    if len(parts) == 2:
                        feet = int(parts[0])
                        inches = int(parts[1])
                        return round((feet * 12 + inches) * 2.54, 1)
                except:
                    return None
        return None
    df[nueva_columna] = df[columna].apply(height_to_cm)
    df = df.drop(columns=[columna])
    return df

def limpiar_columna_joined(df, columna='Joined'):
    """
    Convierte la columna Joined a tipo datetime. Si no puede convertir, pone NaT.
    
    Parámetros:
    df (pd.DataFrame): DataFrame con la columna Joined.
    columna (str): Nombre de la columna a limpiar (por defecto 'Joined').
    
    Retorna:
    pd.DataFrame: DataFrame con la columna Joined en formato datetime.
    """
    df[columna] = pd.to_datetime(df[columna], errors='coerce')
    return df


def limpiar_columnas_dinero(df, columnas):
    """
    Convierte las columnas de dinero a número (euros).
    - Convierte valores con 'K' y 'M' a miles y millones.
    - Elimina el símbolo '€'.
    - Si no puede convertir, deja None.
    - Crea nuevas columnas con sufijo '_eur' y elimina las originales.
    
    Parámetros:
    df (pd.DataFrame): DataFrame con las columnas de dinero.
    columnas (list): Lista de columnas a limpiar.
    
    Retorna:
    pd.DataFrame: DataFrame con columnas de dinero limpias.
    """
    def money_to_float(x):
        if isinstance(x, str):
            x = x.replace('€', '').replace('K', 'e3').replace('M', 'e6')
            try:
                return float(eval(x))
            except:
                return None
        return None

    for col in columnas:
        df[col + '_eur'] = df[col].apply(money_to_float)
    df = df.drop(columns=columnas)
    return df