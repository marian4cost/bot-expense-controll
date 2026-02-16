import os
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

EXCEL_FILE = "controle_financeiro.xlsx"
TELEGRAM_TOKEN = "COLOQUE_SEU_TOKEN_AQUI"

def inicializar_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Data", "Valor", "Categoria", "Descrição"])
        df.to_excel(EXCEL_FILE, index=False)

def adicionar_gasto(valor, categoria, descricao):
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Olá! Use /add valor categoria descrição"
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        _, valor, categoria, *descricao = update.message.text.split()
        descricao = " ".join(descricao)
        adicionar_gasto(valor, categoria, descricao)
        await update.message.reply_text("Gasto registrado!")
    except:
        await update.message.reply_text("Erro. Use /add 50 comida lanche")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add", add))
    app.run_polling()

if __name__ == "__main__":
    main()
