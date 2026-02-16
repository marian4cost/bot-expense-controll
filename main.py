import os
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

PASTA_MESES = "meses"
HISTORICO_FILE = "historico_mensal.xlsx"
TELEGRAM_TOKEN = "COLOQUE_SEU_TOKEN_AQUI"

def inicializar_sistema():
    if not os.path.exists(PASTA_MESES):
        os.makedirs(PASTA_MESES)

    if not os.path.exists(HISTORICO_FILE):
        df = pd.DataFrame(columns=[
            "Mes", "Total_Gastos", "Total_Pagamentos", "Saldo"
        ])
        df.to_excel(HISTORICO_FILE, index=False)


def arquivo_mes(mes=None):
    if mes is None:
        mes = datetime.now().strftime("%Y-%m")
    return os.path.join(PASTA_MESES, f"{mes}.xlsx")


def inicializar_mes():
    file = arquivo_mes()
    if not os.path.exists(file):
        df = pd.DataFrame(columns=["Data", "Tipo", "Valor", "Categoria", "Descrição"])
        df.to_excel(file, index=False)

def adicionar_registro(tipo, valor, categoria, descricao):
    inicializar_sistema()
    inicializar_mes()

    file = arquivo_mes()
    df = pd.read_excel(file)

    novo = {
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Tipo": tipo,
        "Valor": float(valor),
        "Categoria": categoria,
        "Descrição": descricao
    }

    df.loc[len(df)] = novo
    df.to_excel(file, index=False)

def listar_registros_mes():
    inicializar_mes()
    df = pd.read_excel(arquivo_mes())

    if df.empty:
        return (
            "📌 *Registros do Mês*\n\n"
            "❗ Nenhum registro encontrado neste mês."
        )

    texto = "📌 *Registros do Mês*\n\n"
    for _, row in df.iterrows():
        texto += (
            f"• {row['Data']} — *{row['Tipo']}* — R$ {row['Valor']:.2f}\n"
            f"   {row['Categoria']} — {row['Descrição']}\n\n"
        )
    return texto

def totais_mes():
    inicializar_mes()
    df = pd.read_excel(arquivo_mes())

    if df.empty:
        return 0, 0, 0

    total_gastos = df[df["Tipo"] == "Gasto"]["Valor"].sum()
    total_pag = df[df["Tipo"] == "Pagamento"]["Valor"].sum()
    saldo = total_pag - total_gastos

    return total_gastos, total_pag, saldo

def atualizar_historico():
    inicializar_sistema()

    mes = datetime.now().strftime("%Y-%m")
    gastos, pag, saldo = totais_mes()

    hist = pd.read_excel(HISTORICO_FILE)

    if mes in hist["Mes"].values:
        hist.loc[hist["Mes"] == mes, ["Total_Gastos", "Total_Pagamentos", "Saldo"]] = [
            gastos, pag, saldo
        ]
    else:
        novo = {
            "Mes": mes,
            "Total_Gastos": gastos,
            "Total_Pagamentos": pag,
            "Saldo": saldo
        }
        hist = pd.concat([hist, pd.DataFrame([novo])], ignore_index=True)

    hist.to_excel(HISTORICO_FILE, index=False)


def ver_historico():
    df = pd.read_excel(HISTORICO_FILE)

    if df.empty:
        return (
            "📅 *Histórico Mensal*\n\n"
            "❗ Nenhum mês registrado."
        )

    texto = "📅 *Histórico Mensal*\n\n"
    for _, row in df.iterrows():
        texto += (
            f"📌 {row['Mes']}\n"
            f"🔴 Gastos: R$ {row['Total_Gastos']:.2f}\n"
            f"🟢 Pagamentos: R$ {row['Total_Pagamentos']:.2f}\n"
            f"🔵 Saldo: R$ {row['Saldo']:.2f}\n\n"
        )

    return texto

def ver_medias():
    df = pd.read_excel(HISTORICO_FILE)

    if df.empty:
        return (
            "📊 *Médias Gerais*\n\n"
            "❗ Nenhuma média disponível."
        )

    return (
        "📊 *Média Geral dos Meses*\n\n"
        f"🔴 Média de Gastos: R$ {df['Total_Gastos'].mean():.2f}\n"
        f"🟢 Média de Pagamentos: R$ {df['Total_Pagamentos'].mean():.2f}\n"
        f"🔵 Média de Saldo: R$ {df['Saldo'].mean():.2f}"
    )

def resetar_tudo():
    if os.path.exists(PASTA_MESES):
        for f in os.listdir(PASTA_MESES):
            os.remove(os.path.join(PASTA_MESES, f))

    if os.path.exists(HISTORICO_FILE):
        os.remove(HISTORICO_FILE)

    inicializar_sistema()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(menu_text())


def menu_text():
    return (
        "📊 *Controle Financeiro*\n\n"
        "1 – Registrar Gasto\n"
        "2 – Registrar Pagamento\n"
        "3 – Listar Registros do Mês\n"
        "4 – Ver Totais do Mês\n"
        "5 – Ver Histórico Mensal\n"
        "6 – Ver Médias Gerais\n"
        "7 – Resetar Tudo"
    )


# ---------------------------------------
# BOT MENSAGENS
# ---------------------------------------

async def mensagens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.strip().lower()

    if texto == "1":
        context.user_data["modo"] = "gasto"
        await update.message.reply_text("Digite: valor categoria descrição")
        return

    if texto == "2":
        context.user_data["modo"] = "pagamento"
        await update.message.reply_text("Digite: valor categoria descrição")
        return

    if texto == "3":
        await update.message.reply_text(listar_registros_mes(), parse_mode="Markdown")
        return

    if texto == "4":
        gastos, pag, saldo = totais_mes()
        await update.message.reply_text(
            f"🔴 Gastos: R$ {gastos:.2f}\n"
            f"🟢 Pagamentos: R$ {pag:.2f}\n"
            f"🔵 Saldo: R$ {saldo:.2f}"
        )
        return

    if texto == "5":
        await update.message.reply_text(ver_historico(), parse_mode="Markdown")
        return

    if texto == "6":
        await update.message.reply_text(ver_medias(), parse_mode="Markdown")
        return

    if texto == "7":
        resetar_tudo()
        await update.message.reply_text("🗑 Sistema resetado.")
        return

    if "modo" in context.user_data:
        try:
            modo = context.user_data["modo"]
            valor, categoria, *desc = texto.split()
            descricao = " ".join(desc)

            tipo = "Gasto" if modo == "gasto" else "Pagamento"

            adicionar_registro(tipo, valor, categoria, descricao)
            atualizar_historico()

            await update.message.reply_text("✔ Registro adicionado!")
            del context.user_data["modo"]

        except:
            await update.message.reply_text("⚠ Formato inválido. Use: valor categoria descrição")

        return

    await update.message.reply_text(menu_text())


def main():
    print("BOT INICIADO...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagens))

    app.run_polling()


if __name__ == "__main__":
    main()
