import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Sistema 2.0 — Tênis de Mesa",
    page_icon="🏓",
    layout="wide",
)

BASE = Path(__file__).parent

@st.cache_data
def carregar_dados():
    partidas = pd.read_csv(BASE / "partidas.csv")
    sets = pd.read_csv(BASE / "sets.csv")
    jogadores = pd.read_csv(BASE / "jogadores.csv")

    partidas["Data"] = pd.to_datetime(partidas["Data"], dayfirst=True, errors="coerce")
    sets["Data"] = pd.to_datetime(sets["Data"], dayfirst=True, errors="coerce")

    numericas_partidas = [
        "Sets J1", "Sets J2", "Qtd. Sets", "Total Pontos",
        "Pontos J1", "Pontos J2", "Margem J1"
    ]
    numericas_sets = ["Nº Set", "Pontos J1", "Pontos J2", "Diferença J1", "Total Set"]

    for coluna in numericas_partidas:
        partidas[coluna] = pd.to_numeric(partidas[coluna], errors="coerce")

    for coluna in numericas_sets:
        sets[coluna] = pd.to_numeric(sets[coluna], errors="coerce")

    return partidas, sets, jogadores

partidas, sets, jogadores = carregar_dados()

st.title("🏓 Sistema 2.0 — Análise de Tênis de Mesa")
st.caption("Base oficial atual: somente as 30 partidas novas.")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "Dashboard",
        "Jogos do Dia",
        "Análise Individual",
        "H2H",
        "Estatísticas por Set",
        "Partidas",
        "Banco de Dados",
    ],
)

nomes = sorted(set(partidas["Jogador 1"].dropna()) | set(partidas["Jogador 2"].dropna()))

def jogos_do_jogador(nome):
    return partidas[(partidas["Jogador 1"] == nome) | (partidas["Jogador 2"] == nome)].copy()

def visao_jogador(nome):
    jogos = jogos_do_jogador(nome)
    if jogos.empty:
        return None

    jogos["Pontos Feitos"] = jogos.apply(
        lambda r: r["Pontos J1"] if r["Jogador 1"] == nome else r["Pontos J2"], axis=1
    )
    jogos["Pontos Sofridos"] = jogos.apply(
        lambda r: r["Pontos J2"] if r["Jogador 1"] == nome else r["Pontos J1"], axis=1
    )
    jogos["Resultado"] = jogos["Vencedor"].apply(lambda x: "Vitória" if x == nome else "Derrota")
    jogos["Posição"] = jogos["Jogador 1"].apply(lambda x: "Jogador 1" if x == nome else "Jogador 2")
    jogos["Adversário"] = jogos.apply(
        lambda r: r["Jogador 2"] if r["Jogador 1"] == nome else r["Jogador 1"], axis=1
    )
    return jogos

if pagina == "Dashboard":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Partidas oficiais", len(partidas))
    c2.metric("Sets registrados", len(sets))
    c3.metric("Jogadores", len(nomes))
    c4.metric("Média de pontos", f'{partidas["Total Pontos"].mean():.1f}')

    st.subheader("Distribuição das partidas")
    distribuicao = partidas["Qtd. Sets"].value_counts().sort_index()
    st.bar_chart(distribuicao)

    st.subheader("Resumo dos jogadores")
    resumo = []
    for nome in nomes:
        jogos = visao_jogador(nome)
        vitorias = (jogos["Resultado"] == "Vitória").sum()
        resumo.append({
            "Jogador": nome,
            "Partidas": len(jogos),
            "Vitórias": vitorias,
            "Derrotas": len(jogos) - vitorias,
            "Aproveitamento": vitorias / len(jogos) if len(jogos) else 0,
            "Média pontos feitos": jogos["Pontos Feitos"].mean(),
            "Média pontos sofridos": jogos["Pontos Sofridos"].mean(),
        })
    resumo_df = pd.DataFrame(resumo).sort_values(["Aproveitamento", "Partidas"], ascending=False)
    st.dataframe(
        resumo_df.style.format({
            "Aproveitamento": "{:.1%}",
            "Média pontos feitos": "{:.1f}",
            "Média pontos sofridos": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

elif pagina == "Jogos do Dia":
    datas = sorted(partidas["Data"].dropna().dt.date.unique())
    data = st.selectbox("Selecione a data", datas)
    filtro = partidas[partidas["Data"].dt.date == data].copy()
    filtro = filtro.sort_values(["Horário", "Ordem Entrada"])
    st.metric("Partidas no dia", len(filtro))
    st.dataframe(
        filtro[[
            "Horário", "Jogador 1", "Jogador 2", "Sets J1",
            "Sets J2", "Vencedor", "Total Pontos", "Qtd. Sets"
        ]],
        use_container_width=True,
        hide_index=True,
    )

elif pagina == "Análise Individual":
    nome = st.selectbox("Selecione o jogador", nomes)
    jogos = visao_jogador(nome)
    vitorias = (jogos["Resultado"] == "Vitória").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Partidas", len(jogos))
    c2.metric("Vitórias", vitorias)
    c3.metric("Derrotas", len(jogos) - vitorias)
    c4.metric("Aproveitamento", f"{vitorias / len(jogos):.1%}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Média feitos", f'{jogos["Pontos Feitos"].mean():.1f}')
    c6.metric("Média sofridos", f'{jogos["Pontos Sofridos"].mean():.1f}')
    c7.metric("Saldo médio", f'{(jogos["Pontos Feitos"] - jogos["Pontos Sofridos"]).mean():.1f}')
    c8.metric("Média de sets", f'{jogos["Qtd. Sets"].mean():.1f}')

    st.subheader("Desempenho por posição")
    posicao = jogos.groupby("Posição").agg(
        Partidas=("Resultado", "size"),
        Vitórias=("Resultado", lambda x: (x == "Vitória").sum()),
        Média_feitos=("Pontos Feitos", "mean"),
        Média_sofridos=("Pontos Sofridos", "mean"),
    ).reset_index()
    posicao["Aproveitamento"] = posicao["Vitórias"] / posicao["Partidas"]
    st.dataframe(
        posicao.style.format({
            "Aproveitamento": "{:.1%}",
            "Média_feitos": "{:.1f}",
            "Média_sofridos": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Desempenho por set")
    sets_jogador = sets[(sets["Jogador 1"] == nome) | (sets["Jogador 2"] == nome)].copy()
    sets_jogador["Pontos Feitos"] = sets_jogador.apply(
        lambda r: r["Pontos J1"] if r["Jogador 1"] == nome else r["Pontos J2"], axis=1
    )
    sets_jogador["Pontos Sofridos"] = sets_jogador.apply(
        lambda r: r["Pontos J2"] if r["Jogador 1"] == nome else r["Pontos J1"], axis=1
    )
    sets_jogador["Venceu"] = sets_jogador["Vencedor Set"] == nome

    por_set = sets_jogador.groupby("Nº Set").agg(
        Disputados=("Venceu", "size"),
        Vencidos=("Venceu", "sum"),
        Média_feitos=("Pontos Feitos", "mean"),
        Média_sofridos=("Pontos Sofridos", "mean"),
    ).reset_index()
    por_set["Aproveitamento"] = por_set["Vencidos"] / por_set["Disputados"]
    por_set["Saldo"] = por_set["Média_feitos"] - por_set["Média_sofridos"]
    st.dataframe(
        por_set.style.format({
            "Aproveitamento": "{:.1%}",
            "Média_feitos": "{:.1f}",
            "Média_sofridos": "{:.1f}",
            "Saldo": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Histórico")
    st.dataframe(
        jogos[[
            "Data", "Horário", "Posição", "Adversário", "Sets J1",
            "Sets J2", "Resultado", "Pontos Feitos", "Pontos Sofridos"
        ]].sort_values(["Data", "Horário"], ascending=False),
        use_container_width=True,
        hide_index=True,
    )

elif pagina == "H2H":
    c1, c2 = st.columns(2)
    jogador_a = c1.selectbox("Jogador A", nomes, index=0)
    restantes = [n for n in nomes if n != jogador_a]
    jogador_b = c2.selectbox("Jogador B", restantes, index=0)

    h2h = partidas[
        ((partidas["Jogador 1"] == jogador_a) & (partidas["Jogador 2"] == jogador_b)) |
        ((partidas["Jogador 1"] == jogador_b) & (partidas["Jogador 2"] == jogador_a))
    ].copy()

    va = (h2h["Vencedor"] == jogador_a).sum()
    vb = (h2h["Vencedor"] == jogador_b).sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Confrontos", len(h2h))
    m2.metric(f"Vitórias — {jogador_a}", va)
    m3.metric(f"Vitórias — {jogador_b}", vb)

    if h2h.empty:
        st.info("Ainda não existe confronto direto entre esses jogadores na base atual.")
    else:
        h2h["Pontos A"] = h2h.apply(
            lambda r: r["Pontos J1"] if r["Jogador 1"] == jogador_a else r["Pontos J2"], axis=1
        )
        h2h["Pontos B"] = h2h.apply(
            lambda r: r["Pontos J2"] if r["Jogador 1"] == jogador_a else r["Pontos J1"], axis=1
        )

        c4, c5, c6 = st.columns(3)
        c4.metric("Média pontos A", f'{h2h["Pontos A"].mean():.1f}')
        c5.metric("Média pontos B", f'{h2h["Pontos B"].mean():.1f}')
        c6.metric("Média total", f'{h2h["Total Pontos"].mean():.1f}')

        st.dataframe(
            h2h[[
                "Data", "Horário", "Jogador 1", "Jogador 2",
                "Sets J1", "Sets J2", "Vencedor", "Total Pontos"
            ]].sort_values(["Data", "Horário"], ascending=False),
            use_container_width=True,
            hide_index=True,
        )

elif pagina == "Estatísticas por Set":
    st.subheader("Médias gerais por número do set")
    geral = sets.groupby("Nº Set").agg(
        Quantidade=("ID Set", "count"),
        Média_total=("Total Set", "mean"),
        Média_J1=("Pontos J1", "mean"),
        Média_J2=("Pontos J2", "mean"),
    ).reset_index()
    st.dataframe(
        geral.style.format({
            "Média_total": "{:.1f}",
            "Média_J1": "{:.1f}",
            "Média_J2": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
    st.line_chart(geral.set_index("Nº Set")[["Média_total"]])

elif pagina == "Partidas":
    st.subheader("30 partidas oficiais")
    st.dataframe(
        partidas.sort_values(["Data", "Horário"]),
        use_container_width=True,
        hide_index=True,
    )

elif pagina == "Banco de Dados":
    st.success("O sistema está utilizando apenas a nova base oficial.")
    st.write(f"**Partidas:** {len(partidas)}")
    st.write(f"**Sets:** {len(sets)}")
    st.write(f"**Jogadores:** {len(nomes)}")
    st.caption("Para adicionar novas partidas, atualize partidas.csv e sets.csv mantendo os mesmos cabeçalhos.")
    st.download_button(
        "Baixar partidas.csv",
        (BASE / "partidas.csv").read_bytes(),
        file_name="partidas.csv",
        mime="text/csv",
    )
    st.download_button(
        "Baixar sets.csv",
        (BASE / "sets.csv").read_bytes(),
        file_name="sets.csv",
        mime="text/csv",
    )
