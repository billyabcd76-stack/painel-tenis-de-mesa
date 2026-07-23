# Sistema 2.0 — Tênis de Mesa

Projeto pronto para usar somente as 30 partidas oficiais da nova base.

## Arquivos

- `app.py`: painel Streamlit.
- `partidas.csv`: 30 partidas oficiais.
- `sets.csv`: 113 sets.
- `jogadores.csv`: cadastro e resumo dos jogadores.
- `requirements.txt`: dependências.

## Rodar no computador

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud

1. Envie todos os arquivos para um repositório no GitHub.
2. No Streamlit Community Cloud, selecione o repositório.
3. Informe `app.py` como arquivo principal.
4. Clique em Deploy.

A base antiga de 102 partidas não está incluída e não será contada.
