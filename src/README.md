# Código da Aplicação

Esta pasta contém o código do agente financeiro **Leofi**.

## Estrutura

```
src/
├── app.py              # Aplicação principal (Streamlit + Ollama)
└── requirements.txt    # Dependências do projeto
```

## Dependências

```
streamlit==1.45.0
requests==2.32.3
pandas==2.2.3
```

## Como Rodar

### 1. Certifique-se que o Ollama está rodando

```bash
# Baixe o Ollama em: https://ollama.com
ollama pull llama3
ollama serve
```

> Você pode substituir `llama3` por qualquer outro modelo disponível no Ollama. Basta atualizar a variável `MODELO` no `app.py`.

### 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 3. Rodar o Leofi

Execute a partir da **raiz do projeto**:

```bash
streamlit run src/app.py
```

> ⚠️ É importante rodar a partir da raiz para que os caminhos `./data/` sejam resolvidos corretamente.

## O que o `app.py` faz

- Carrega os 8 arquivos de dados da pasta `data/` (JSON e CSV)
- Calcula automaticamente a margem disponível do cliente
- Monta o contexto personalizado a cada chamada ao LLM
- Mantém o histórico da conversa durante a sessão
- Renderiza a interface de chat via Streamlit
- Trata erros de conexão com o Ollama de forma amigável
