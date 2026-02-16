import os
import pandas as pd
from datetime import datetime

EXCEL_FILE = "controle_financeiro.xlsx"

def inicializar_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Data", "Valor", "Categoria", "Descrição"])
        df.to_excel(EXCEL_FILE, index=False)

def adicionar_registro(valor, categoria, descricao):
    inicializar_excel()
    df = pd.read_excel(EXCEL_FILE)

    novo = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Valor": float(valor),
        "Categoria": categoria,
        "Descrição": descricao
    }

    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

def listar_registros():
    inicializar_excel()
    df = pd.read_excel(EXCEL_FILE)
    return df
