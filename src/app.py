import json
import pandas as pd
import requests
import streamlit as st

# ============ CONFIGURAÇÃO ============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "llama3"  # troque pelo modelo que você tiver instalado no Ollama

# ============ CARREGAR DADOS ============
perfil    = json.load(open('./data/perfil_investidor.json', encoding='utf-8'))
dividas   = json.load(open('./data/dividas.json', encoding='utf-8'))
despesas  = json.load(open('./data/despesas_fixas.json', encoding='utf-8'))
produtos  = json.load(open('./data/produtos_financeiros.json', encoding='utf-8'))
regras    = json.load(open('./data/simulacoes_regras.json', encoding='utf-8'))

transacoes = pd.read_csv('./data/transacoes.csv')
historico  = pd.read_csv('./data/historico_atendimento.csv')

# ============ CALCULAR MARGEM DISPONÍVEL ============
total_despesas_fixas = sum(despesas.values())
parcela_emprestimo   = next(
    (d['valor_parcela'] for d in dividas if d['tipo'] == 'emprestimo_pessoal'), 0
)
margem_estimada = perfil['renda_mensal'] - total_despesas_fixas - parcela_emprestimo

# ============ MONTAR CONTEXTO ============
def montar_contexto():
    return f"""
PERFIL DO CLIENTE:
- Nome: {perfil['nome']}, {perfil['idade']} anos — {perfil['profissao']}
- Perfil investidor: {perfil['perfil_investidor']} | Aceita risco: {'Sim' if perfil['aceita_risco'] else 'Não'}
- Renda mensal: R$ {perfil['renda_mensal']:,.2f}
- Patrimônio total: R$ {perfil['patrimonio_total']:,.2f}
- Reserva de emergência atual: R$ {perfil['reserva_emergencia_atual']:,.2f}
- Objetivo principal: {perfil['objetivo_principal']}

METAS FINANCEIRAS:
{chr(10).join([f"- {m['meta']}: R$ {m['valor_necessario']:,.2f} até {m['prazo']}" for m in perfil['metas']])}

DÍVIDAS ATIVAS:
{chr(10).join([
    f"- Cartão de crédito: R$ {d['valor_atual']:,.2f} | Juros: {d['juros_mensal']*100:.0f}% a.m. | Vence dia {d['dia_vencimento']}"
    if d['tipo'] == 'cartao_credito'
    else f"- Empréstimo pessoal: {d['parcelas_restantes']}x R$ {d['valor_parcela']:,.2f} restantes | Juros total: {d['juros_total']*100:.0f}%"
    for d in dividas
])}

DESPESAS FIXAS MENSAIS:
{chr(10).join([f"- {k.capitalize()}: R$ {v:,.2f}" for k, v in despesas.items()])}
- Total fixo: R$ {total_despesas_fixas:,.2f}

MARGEM DISPONÍVEL ESTIMADA:
- Renda R$ {perfil['renda_mensal']:,.2f} - Despesas fixas R$ {total_despesas_fixas:,.2f} - Parcela empréstimo R$ {parcela_emprestimo:,.2f}
- Margem: ~R$ {margem_estimada:,.2f} por mês (antes de gastos variáveis)

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

HISTÓRICO DE ATENDIMENTO:
{historico.to_string(index=False)}

PRODUTOS FINANCEIROS DISPONÍVEIS:
{json.dumps([p for p in produtos if isinstance(p, dict) and 'nome' in p], indent=2, ensure_ascii=False)}

REGRAS DE SIMULAÇÃO:
{json.dumps(regras, indent=2, ensure_ascii=False)}
"""

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """Você é o Leofi, um assistente financeiro pessoal amigável e empático.

OBJETIVO:
Ajudar o usuário a organizar sua vida financeira por meio de linguagem natural,
simulações práticas e explicações claras — orientando, nunca decidindo.

REGRAS:
- NUNCA recomende investimentos específicos; apenas explique como funcionam;
- JAMAIS responda a perguntas fora do tema finanças pessoais.
  Quando ocorrer, responda lembrando o seu papel de assistente financeiro;
- Use SEMPRE os dados fornecidos no contexto para personalizar as respostas;
- Se não souber algo, admita: "Não tenho essa informação, mas posso te ajudar com...";
- Linguagem simples e próxima, como se fosse um amigo que entende de finanças;
- Nunca julgue os gastos ou decisões financeiras do usuário;
- Responda de forma direta e objetiva, com no máximo 3 parágrafos;
- Quando fizer simulações, mostre os cálculos de forma clara e passo a passo;
- Ao final de respostas mais longas, pergunte se o usuário quer aprofundar algum ponto.

EXEMPLOS DE INTERAÇÃO (few-shot):

Pergunta: "Quanto tempo vou levar para completar minha reserva de emergência?"
Resposta: "Sua reserva atual é de R$ 10.000 e sua meta é R$ 15.000 — faltam R$ 5.000.
Com uma margem mensal estimada de R$ 1.940 (após despesas fixas e parcela do empréstimo),
se você guardar R$ 500/mês, levaria 10 meses. Se guardar R$ 1.000/mês, chegaria lá em 5 meses.
Quer que eu simule outros valores?"

Pergunta: "O que é Tesouro Selic?"
Resposta: "O Tesouro Selic é um título público emitido pelo governo federal. Ele rende
100% da taxa Selic, que hoje é a taxa básica de juros do Brasil. É considerado o
investimento mais seguro do país, tem liquidez diária e o aporte mínimo é de apenas R$ 30.
É muito indicado para quem está montando reserva de emergência — exatamente o seu objetivo atual!"

Pergunta: "Onde devo investir meu dinheiro agora?"
Resposta: "Não tenho como te dizer onde investir — isso é responsabilidade de um consultor
financeiro certificado. O que posso fazer é te explicar como cada produto funciona para
que você tome a decisão com mais clareza. Quer que eu explique as diferenças entre
Tesouro Selic, CDB e LCI/LCA?"
"""

# ============ CHAMAR OLLAMA ============
def perguntar(msg: str, historico_chat: list) -> str:
    contexto = montar_contexto()

    # Monta o histórico da conversa atual para dar continuidade
    historico_formatado = ""
    for turno in historico_chat[-6:]:  # últimos 3 pares de mensagens
        role = "Usuário" if turno["role"] == "user" else "Leofi"
        historico_formatado += f"\n{role}: {turno['content']}"

    prompt = f"""{SYSTEM_PROMPT}

CONTEXTO DO CLIENTE:
{contexto}

HISTÓRICO DA CONVERSA ATUAL:{historico_formatado}

Usuário: {msg}
Leofi:"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={"model": MODELO, "prompt": prompt, "stream": False},
            timeout=600
        )
        r.raise_for_status()
        return r.json().get('response', 'Não consegui gerar uma resposta. Tente novamente.')
    except requests.exceptions.ConnectionError:
        return "⚠️ Não consegui me conectar ao Ollama. Verifique se ele está rodando com `ollama serve`."
    except requests.exceptions.Timeout:
        return "⏱️ A resposta demorou demais. Tente novamente com uma pergunta mais curta."
    except Exception as e:
        return f"❌ Ocorreu um erro inesperado: {str(e)}"

# ============ INTERFACE STREAMLIT ============
st.set_page_config(
    page_title="Leofi — Assistente Financeiro",
    page_icon="💰",
    layout="centered"
)

# Cabeçalho
st.title("💰 Leofi")
st.caption("Seu assistente financeiro pessoal — orienta, não decide.")

# Inicializa histórico da sessão
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensagem de boas-vindas automática
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            f"Oi, {perfil['nome'].split()[0]}! 👋 Sou o Leofi, seu assistente financeiro pessoal. "
            f"Posso te ajudar a organizar suas finanças, simular metas ou entender melhor seus investimentos. "
            f"Por onde quer começar?"
        )
    })

# Exibe histórico de mensagens
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Input do usuário
if pergunta := st.chat_input("Digite sua dúvida financeira..."):
    # Adiciona mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": pergunta})
    st.chat_message("user").write(pergunta)

    # Gera e exibe resposta
    with st.spinner("Leofi está pensando..."):
        resposta = perguntar(pergunta, st.session_state.messages[:-1])

    st.session_state.messages.append({"role": "assistant", "content": resposta})
    st.chat_message("assistant").write(resposta)

# Rodapé com botão de limpar conversa
st.divider()
col1, col2 = st.columns([4, 1])
with col1:
    st.caption("⚠️ O Leofi é um assistente educativo e não substitui um consultor financeiro certificado.")
with col2:
    if st.button("🗑️ Limpar"):
        st.session_state.messages = []
        st.rerun()
