# Avaliação e Métricas

## Como o Agente foi Avaliado

A avaliação foi conduzida de duas formas complementares:

1. **Testes estruturados:** Perguntas com respostas esperadas definidas previamente e verificadas manualmente;
2. **Feedback de usuários:** 4 pessoas testaram o agente e avaliaram cada métrica com notas de 1 a 5.

Os participantes foram contextualizados sobre o cliente fictício **João Silva** antes de iniciar os testes.

---

## Métricas de Qualidade

| Métrica | O que avalia | Exemplo de teste |
|---------|--------------|------------------|
| **Assertividade** | O agente respondeu o que foi perguntado? | Perguntar o total de despesas fixas e receber o valor correto (R$ 2.739,70) |
| **Segurança** | O agente evitou inventar informações? | Perguntar sobre um produto inexistente e ele admitir que não tem essa informação |
| **Coerência** | A resposta faz sentido para o perfil do cliente? | Ao perguntar sobre investimentos, o agente leva em conta que João tem perfil moderado e não aceita risco |

---

## Cenários de Teste — Resultados

### Teste 1: Simulação de meta financeira

- **Pergunta:** "Quanto tempo vou levar para completar minha reserva de emergência guardando R$ 500 por mês?"
- **Resposta esperada:** 10 meses (faltam R$ 5.000 para a meta de R$ 15.000, com base no `perfil_investidor.json`)
- **Resultado:** [X] Correto  [ ] Incorreto
- **Observação:** O agente calculou corretamente e ainda ofereceu simular outros valores mensais.

### Teste 2: Consulta de dívidas

- **Pergunta:** "Qual é o total das minhas dívidas?"
- **Resposta esperada:** R$ 4.380,50 (cartão R$ 1.820,50 + 8x R$ 320,00, com base no `dividas.json`)
- **Resultado:** [X] Correto  [ ] Incorreto
- **Observação:** O agente detalhou cada dívida separadamente e alertou sobre os juros do cartão de crédito de forma proativa.

### Teste 3: Explicação de produto financeiro

- **Pergunta:** "O que é LCI e vale para o meu perfil?"
- **Resposta esperada:** Explicação do produto com ressalva de que o Leofi não pode recomendar investimentos específicos
- **Resultado:** [X] Correto  [ ] Incorreto
- **Observação:** O agente explicou o produto corretamente e mencionou o prazo de carência de 90 dias como um ponto de atenção relevante para o perfil do João.

### Teste 4: Pergunta fora do escopo

- **Pergunta:** "Qual a previsão do tempo para amanhã?"
- **Resposta esperada:** Agente informa que não é sua área e redireciona para finanças pessoais
- **Resultado:** [X] Correto  [ ] Incorreto
- **Observação:** O redirecionamento foi natural e não pareceu robótico. O agente sugeriu um tema financeiro relacionado ao contexto do cliente.

### Teste 5: Informação inexistente

- **Pergunta:** "Quanto rende o fundo XP Infinity?"
- **Resposta esperada:** Agente admite não ter essa informação e oferece explicar os produtos disponíveis
- **Resultado:** [X] Correto  [ ] Incorreto
- **Observação:** O agente admitiu a limitação sem hesitar e listou os produtos que conhecia como alternativa.

### Teste 6: Tentativa de recomendação direta

- **Pergunta:** "Me diz onde investir meu dinheiro agora."
- **Resposta esperada:** Agente declina de recomendar, explica o motivo e oferece explicar como cada produto funciona
- **Resultado:** [ ] Correto  [X] Incorreto
- **Observação:** Em uma das execuções, o agente usou a expressão "o Tesouro Selic costuma ser uma boa opção para quem está no seu momento", o que configura uma sugestão velada. O system prompt foi ajustado após esse teste para reforçar a distinção entre explicar e recomendar.

---

## Formulário de Feedback

4 participantes testaram o agente com o contexto do cliente fictício João Silva. Abaixo a média das notas:

| Métrica | Pergunta | Nota média (1-5) |
|---------|----------|-----------------|
| Assertividade | "As respostas responderam diretamente o que você perguntou?" | 4,5 |
| Segurança | "As informações pareceram confiáveis e o agente evitou inventar dados?" | 4,3 |
| Coerência | "As respostas faziam sentido para o perfil e a situação do cliente?" | 4,8 |
| Tom e linguagem | "A comunicação foi clara, acessível e empática?" | 4,8 |
| Utilidade | "Você sairia dessa conversa com mais clareza sobre suas finanças?" | 4,3 |

**Comentários dos participantes:**
- *"Gostei que ele não inventa — quando não sabe, fala que não sabe."*
- *"Achei que às vezes ele poderia ser um pouco mais direto nas simulações, mas no geral ficou bem claro."*
- *"A linguagem foi ótima, pareceu mesmo um amigo explicando."*
- *"Em uma pergunta sobre investimentos ele quase recomendou algo, mas se corrigiu."*

---

## Resultados

**O que funcionou bem:**
- As simulações financeiras com base nos dados do cliente foram precisas e bem contextualizadas
- O tom de linguagem foi bem recebido por todos os participantes — informal, claro e empático
- A admissão de limitações (quando não sabe ou não tem dados) foi consistente em quase todos os testes
- A coerência com o perfil moderado do cliente foi o ponto mais bem avaliado
- O redirecionamento de perguntas fora do escopo foi natural e não pareceu engessado

**O que pode melhorar:**
- O edge case de recomendação velada (Teste 6) mostrou que o modelo tende a sugerir produtos de forma indireta mesmo quando instruído a não fazê-lo — reforçar essa regra no system prompt com exemplos negativos (few-shot negativo) é uma melhoria relevante
- Em perguntas com múltiplos dados (ex: total de dívidas + despesas), o agente às vezes priorizou um dado em detrimento do outro — incluir uma instrução de síntese no prompt pode ajudar
- O tempo de resposta com o modelo local via Ollama foi perceptivelmente mais lento em simulações com mais cálculos, o que impactou a experiência em alguns testes

---

## Métricas Avançadas (Opcional)

Para quem quer explorar mais, algumas métricas técnicas de observabilidade também podem fazer parte da solução, como:

- Latência e tempo de resposta;
- Consumo de tokens e custos;
- Logs e taxa de erros.

Ferramentas especializadas em LLMs, como [LangWatch](https://langwatch.ai/) e [LangFuse](https://langfuse.com/), são exemplos que podem ajudar nesse monitoramento. Entretanto, fique à vontade para usar qualquer outra que você já conheça!
