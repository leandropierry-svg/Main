"""
SIMULADOR da Eletrofilms - roda só com Python, sem WhatsApp e sem instalar nada.
Serve para testar as respostas e o fluxo de atendimento no terminal.

Rodar:
    python teste_eletrofilms.py
"""

import csv
import os
from datetime import datetime


NUMERO_DONO = "5511999999999"  # número fictício só para simular o aviso ao dono
ARQUIVO_LEADS = "clientes_eletrofilms.csv"

# Estado da conversa de cada cliente (em memória).
# Para produção, troque por Redis ou banco de dados.
sessoes = {}

# ----------------------------------------------------------------------
# TEXTOS
# ----------------------------------------------------------------------
MENU = (
    "Olá! 👋 Bem-vindo à *Eletrofilms* - Serviços Automotivos 🚗✨\n"
    "Somos especialistas em aplicação de películas.\n\n"
    "Como posso te ajudar? Responda com o número:\n\n"
    "1️⃣ Película *Window Blue*\n"
    "2️⃣ Película *Nano Carbono*\n"
    "3️⃣ Valor do *parabrisa*\n"
    "4️⃣ Quero *agendar / fazer orçamento*\n"
    "5️⃣ Falar com um *atendente*\n\n"
    "_Digite 0 a qualquer momento para voltar a este menu._"
)

TXT_WINDOW_BLUE = (
    "💙 *Window Blue* - Bluetech\n\n"
    "• Qualidade *premium*\n"
    "• Alta *retenção de calor*\n"
    "• *5 anos de garantia*\n"
    "• Valor: *R$ 399,00* para carro pequeno (sem incluir o parabrisa)\n\n"
    "Para carros maiores o valor pode variar, é só me informar o modelo."
)

TXT_NANO_CARBONO = (
    "🖤 *Nano Carbono* - Bluetech\n\n"
    "• Qualidade *premium*\n"
    "• Alta *retenção de calor*\n"
    "• *5 anos de garantia*\n"
    "• Valor: *a partir de R$ 250,00* (sem incluir o parabrisa)\n\n"
    "O valor final depende do modelo do carro."
)

TXT_PARABRISA = (
    "🚘 *Parabrisa*\n\n"
    "Se você quiser incluir o parabrisa, o valor é adicional e muda conforme o carro:\n"
    "• De *R$ 80,00 até R$ 120,00* (somente o parabrisa)\n\n"
    "Me diga o modelo do seu carro que informo o valor certinho!"
)

PERGUNTA_INTENCAO = (
    "\n\n──────────────\n"
    "Posso te ajudar com mais alguma coisa?\n"
    "1️⃣ *Quero agendar / orçamento*\n"
    "2️⃣ Só estava tirando dúvidas por enquanto\n"
    "0️⃣ Voltar ao menu"
)

TXT_SO_DUVIDA = (
    "Sem problema nenhum! 😊 Fico feliz em ter ajudado.\n"
    "Quando decidir fazer a película do seu carro, é só chamar por aqui.\n"
    "A *Eletrofilms* agradece o contato! 🚗💙\n\n"
    "Digite *0* para ver o menu novamente."
)


# ----------------------------------------------------------------------
# ENVIO DE MENSAGENS
# ----------------------------------------------------------------------
def enviar(numero, texto):
    """Versão de teste: em vez de mandar pelo WhatsApp, mostra na tela."""
    if numero == NUMERO_DONO:
        print("\n📲 [AVISO QUE O DONO RECEBERIA NO WHATSAPP]")
    else:
        print("\n🤖 ROBÔ:")
    print(texto)


def salvar_lead(numero, dados):
    """Salva o cliente interessado em uma planilha CSV e avisa o dono."""
    novo = not os.path.exists(ARQUIVO_LEADS)
    with open(ARQUIVO_LEADS, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        if novo:
            w.writerow(["data", "whatsapp", "nome", "carro", "pelicula", "parabrisa", "periodo"])
        w.writerow([
            datetime.now().strftime("%d/%m/%Y %H:%M"),
            numero,
            dados.get("nome", ""),
            dados.get("carro", ""),
            dados.get("pelicula", ""),
            dados.get("parabrisa", ""),
            dados.get("periodo", ""),
        ])

    if NUMERO_DONO:
        enviar(
            NUMERO_DONO,
            "🔔 *NOVO CLIENTE - Eletrofilms*\n\n"
            f"👤 Nome: {dados.get('nome')}\n"
            f"📱 WhatsApp: {numero}\n"
            f"🚗 Carro: {dados.get('carro')}\n"
            f"🎞️ Película: {dados.get('pelicula')}\n"
            f"🪟 Parabrisa: {dados.get('parabrisa')}\n"
            f"🕒 Período: {dados.get('periodo')}",
        )


# ----------------------------------------------------------------------
# LÓGICA DA CONVERSA
# ----------------------------------------------------------------------
def processar(numero, texto):
    t = texto.strip().lower()
    s = sessoes.setdefault(numero, {"etapa": "menu", "dados": {}})

    # Volta ao menu a qualquer momento
    if t in ("0", "menu", "oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "início", "inicio"):
        s["etapa"] = "menu"
        s["dados"] = {}
        return enviar(numero, MENU)

    etapa = s["etapa"]

    # ---------------- MENU ----------------
    if etapa == "menu":
        if t == "1":
            s["dados"]["pelicula"] = "Window Blue"
            s["etapa"] = "pos_info"
            return enviar(numero, TXT_WINDOW_BLUE + PERGUNTA_INTENCAO)
        if t == "2":
            s["dados"]["pelicula"] = "Nano Carbono"
            s["etapa"] = "pos_info"
            return enviar(numero, TXT_NANO_CARBONO + PERGUNTA_INTENCAO)
        if t == "3":
            s["etapa"] = "pos_info"
            return enviar(numero, TXT_PARABRISA + PERGUNTA_INTENCAO)
        if t == "4":
            return iniciar_agendamento(numero, s)
        if t == "5":
            s["etapa"] = "humano"
            return enviar(
                numero,
                "Certo! 🙋 Já avisei nossa equipe. Em instantes um atendente "
                "vai falar com você por aqui.\n\n_Digite 0 para voltar ao menu._",
            ) or avisar_humano(numero)
        return enviar(numero, "Não entendi 😅 Escolha uma das opções abaixo:\n\n" + MENU)

    # ------- DEPOIS DE VER UMA INFORMAÇÃO: separa cliente x curioso -------
    if etapa == "pos_info":
        if t == "1":
            return iniciar_agendamento(numero, s)
        if t == "2":
            s["etapa"] = "menu"
            return enviar(numero, TXT_SO_DUVIDA)
        return enviar(numero, "Responda *1* para agendar/orçamento, *2* se for só dúvida ou *0* para o menu.")

    # ---------------- AGENDAMENTO ----------------
    if etapa == "ag_nome":
        s["dados"]["nome"] = texto.strip().title()
        s["etapa"] = "ag_carro"
        return enviar(numero, f"Prazer, {s['dados']['nome']}! 🤝\n\nQual é o *modelo e ano* do seu carro? (ex: Gol 2015)")

    if etapa == "ag_carro":
        s["dados"]["carro"] = texto.strip()
        if s["dados"].get("pelicula"):
            s["etapa"] = "ag_parabrisa"
            return enviar(numero, pergunta_parabrisa())
        s["etapa"] = "ag_pelicula"
        return enviar(
            numero,
            "Qual película você deseja?\n\n1️⃣ Window Blue (R$ 399,00 carro pequeno)\n"
            "2️⃣ Nano Carbono (a partir de R$ 250,00)\n3️⃣ Ainda não sei, quero uma indicação",
        )

    if etapa == "ag_pelicula":
        opcoes = {"1": "Window Blue", "2": "Nano Carbono", "3": "Quer indicação"}
        if t not in opcoes:
            return enviar(numero, "Responda *1*, *2* ou *3* 😉")
        s["dados"]["pelicula"] = opcoes[t]
        s["etapa"] = "ag_parabrisa"
        return enviar(numero, pergunta_parabrisa())

    if etapa == "ag_parabrisa":
        if t not in ("1", "2"):
            return enviar(numero, "Responda *1* (com parabrisa) ou *2* (sem parabrisa).")
        s["dados"]["parabrisa"] = "Sim" if t == "1" else "Não"
        s["etapa"] = "ag_periodo"
        return enviar(
            numero,
            "Qual o melhor período para você?\n\n1️⃣ Manhã\n2️⃣ Tarde\n3️⃣ Qualquer horário",
        )

    if etapa == "ag_periodo":
        periodos = {"1": "Manhã", "2": "Tarde", "3": "Qualquer horário"}
        if t not in periodos:
            return enviar(numero, "Responda *1*, *2* ou *3* 😉")
        s["dados"]["periodo"] = periodos[t]
        salvar_lead(numero, s["dados"])
        s["etapa"] = "humano"
        d = s["dados"]
        return enviar(
            numero,
            "✅ *Pedido recebido!*\n\n"
            f"👤 {d['nome']}\n🚗 {d['carro']}\n🎞️ {d['pelicula']}\n"
            f"🪟 Parabrisa: {d['parabrisa']}\n🕒 {d['periodo']}\n\n"
            "Nossa equipe vai te chamar em breve para confirmar o valor final e o horário. "
            "Obrigado por escolher a *Eletrofilms*! 💙🚗",
        )

    # ---------------- ATENDIMENTO HUMANO ----------------
    if etapa == "humano":
        # O bot fica em silêncio para o atendente conversar.
        # Digite "0" para o cliente reiniciar o menu.
        return

    # Qualquer outro caso
    s["etapa"] = "menu"
    enviar(numero, MENU)


def pergunta_parabrisa():
    return (
        "Deseja incluir o *parabrisa*?\n"
        "(adicional de R$ 80,00 a R$ 120,00 conforme o carro)\n\n"
        "1️⃣ Sim, incluir\n2️⃣ Não, só os vidros laterais/traseiro"
    )


def iniciar_agendamento(numero, s):
    s["etapa"] = "ag_nome"
    return enviar(numero, "Ótimo! Vamos agilizar seu orçamento 🚀\n\nQual é o seu *nome*?")


def avisar_humano(numero):
    if NUMERO_DONO:
        enviar(NUMERO_DONO, f"🙋 Cliente pediu atendimento humano: wa.me/{numero}")


# ----------------------------------------------------------------------
# SIMULADOR DE CONVERSA NO TERMINAL
# ----------------------------------------------------------------------
if __name__ == "__main__":
    NUMERO_CLIENTE = "5511988887777"  # cliente fictício
    print("=" * 60)
    print(" SIMULADOR - Chat Eletrofilms (teste sem WhatsApp)")
    print(" Digite como se fosse o cliente. Para sair: sair")
    print("=" * 60)
    print("Dica: comece digitando 'oi'")

    while True:
        try:
            msg = input("\n👤 VOCÊ: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if msg.lower() in ("sair", "exit", "quit"):
            break
        if msg:
            processar(NUMERO_CLIENTE, msg)

    print("\nTeste encerrado. Se houve agendamento, veja o arquivo", ARQUIVO_LEADS)
