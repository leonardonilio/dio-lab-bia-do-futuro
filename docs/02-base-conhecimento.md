# Base de Conhecimento
 
## Dados Utilizados
 
| Arquivo | Formato | Utilização no Leofi |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores para dar continuidade ao atendimento de forma mais eficiente |
| `perfil_investidor.json` | JSON | Personalizar simulações e explicações com base no perfil, renda, objetivos e metas do cliente |
| `produtos_financeiros.json` | JSON | Explicar produtos disponíveis de acordo com o perfil e objetivo do cliente |
| `transacoes.csv` | CSV | Analisar padrão de gastos e usar essas informações em simulações e orientações práticas |
| `dividas.json` | JSON | Mapear dívidas ativas para calcular impacto no orçamento e priorização de pagamentos |
| `despesas_fixas.json` | JSON | Calcular o total de comprometimento mensal e identificar margem disponível para metas |
| `simulacoes_regras.json` | JSON | Aplicar fórmulas de juros simples, compostos, metas e parcelamentos nas simulações |
| `estado_conversa.json` | JSON | Manter contexto entre turnos da conversa (intenção, valor, prazo, última simulação) |
 
 
---
 
## Adaptações nos Dados
 
> Você modificou ou expandiu os dados mockados? Descreva aqui.
 
Foram adicionados quatro arquivos que não existiam no conjunto original: `dividas.json`, `despesas_fixas.json`, `simulacoes_regras.json` e `estado_conversa.json`. Essas expansões foram necessárias para cobrir funcionalidades centrais do Leofi, como cálculo de margem disponível, simulações financeiras e manutenção de contexto conversacional.
 
No `produtos_financeiros.json`, o Fundo Multimercado foi substituído pelo Fundo Imobiliário (FII), produto mais familiar para o perfil moderado do cliente de referência e mais adequado ao objetivo de renda recorrente.
 
---
 
## Estratégia de Integração
 
### Como os dados são carregados?
 
> Descreva como seu agente acessa a base de conhecimento.
 
Os arquivos JSON e CSV são carregados no início da sessão via código Python e incluídos diretamente no contexto enviado ao LLM. Não há consulta dinâmica a banco de dados — todos os dados são lidos de uma vez e formatados como texto estruturado no prompt.
 
```python
import json
import pandas as pd
 
perfil    = json.load(open('./data/perfil_investidor.json'))
dividas   = json.load(open('./data/dividas.json'))
despesas  = json.load(open('./data/despesas_fixas.json'))
produtos  = json.load(open('./data/produtos_financeiros.json'))
regras    = json.load(open('./data/simulacoes_regras.json'))
estado    = json.load(open('./data/estado_conversa.json'))
 
transacoes = pd.read_csv('./data/transacoes.csv')
historico  = pd.read_csv('./data/historico_atendimento.csv')
```
 
### Como os dados são usados no prompt?
 
> Os dados vão no system prompt? São consultados dinamicamente?
 
Para simplificar, os dados são injetados diretamente no prompt a cada chamada ao LLM, garantindo que o agente tenha o contexto mais completo possível. O system prompt define o comportamento e as regras do Leofi, enquanto o contexto do cliente (dados carregados) é passado junto à mensagem do usuário.
 
Em soluções mais robustas, o ideal seria carregar os dados dinamicamente (ex: por ID de cliente), mas para o escopo deste projeto a injeção estática é suficiente e mais fácil de validar.
 
```python
contexto = f"""
PERFIL DO CLIENTE:
{json.dumps(perfil, indent=2, ensure_ascii=False)}
 
DÍVIDAS ATIVAS:
{json.dumps(dividas, indent=2, ensure_ascii=False)}
 
DESPESAS FIXAS MENSAIS:
{json.dumps(despesas, indent=2, ensure_ascii=False)}
 
TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}
 
HISTÓRICO DE ATENDIMENTO:
{historico.to_string(index=False)}
 
PRODUTOS FINANCEIROS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
 
REGRAS DE SIMULAÇÃO:
{json.dumps(regras, indent=2, ensure_ascii=False)}
 
ESTADO DA CONVERSA:
{json.dumps(estado, indent=2, ensure_ascii=False)}
"""
```
 
---
 
## Exemplo de Contexto Montado
 
> Mostre um exemplo de como os dados são formatados para o agente.
 
O exemplo abaixo sintetiza os dados mais relevantes para otimizar o consumo de tokens, mantendo todas as informações necessárias para que o Leofi responda com precisão e personalização.
 
```
PERFIL DO CLIENTE:
- Nome: João Silva, 32 anos — Analista de Sistemas
- Perfil: Moderado | Aceita risco: Não
- Renda mensal: R$ 5.000
- Patrimônio total: R$ 15.000 | Reserva atual: R$ 10.000 (meta: R$ 15.000)
- Meta 1: Completar reserva de emergência → R$ 5.000 faltando até jun/2026
- Meta 2: Entrada do apartamento → R$ 50.000 até dez/2027
 
DÍVIDAS ATIVAS:
- Cartão de crédito: R$ 1.820,50 (juros 13% a.m., vence dia 10)
- Empréstimo pessoal: 8x R$ 320,00 restantes (juros total 18%)
 
DESPESAS FIXAS MENSAIS:
- Moradia: R$ 1.380 | Alimentação: R$ 550 | Transporte: R$ 300
- Internet: R$ 120 | Energia: R$ 180 | Água: R$ 70
- Academia: R$ 89,90 | Telefonia: R$ 49,90
- Total fixo: R$ 2.739,70
 
MARGEM DISPONÍVEL ESTIMADA:
- Renda: R$ 5.000 - Despesas fixas: R$ 2.739,70 - Parcela empréstimo: R$ 320
- Margem: ~R$ 1.940,30 por mês (antes de gastos variáveis)
 
HISTÓRICO RECENTE:
- Out/25: acompanhou progresso da reserva de emergência
- Out/25: perguntou sobre Tesouro Selic
- Set/25: perguntou sobre CDB e rentabilidade
 
PRODUTOS DISPONÍVEIS PARA EXPLICAR:
- Tesouro Selic — risco baixo | 100% da Selic | Aporte mín. R$ 30
- CDB Liquidez Diária — risco baixo | 102% CDI | Aporte mín. R$ 100
- LCI/LCA — risco baixo | 95% CDI | Aporte mín. R$ 1.000 (isento de IR)
- FII — risco médio | DY 6% a 12% a.a. | Aporte mín. R$ 100
- Fundo de Ações — risco alto | variável | Aporte mín. R$ 100
```
