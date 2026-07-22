import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Painel Tênis de Mesa",
    page_icon="🏓",
    layout="wide",
)

st.markdown("""
<style>
.stApp { background: #07111f; color: #eef4ff; }
[data-testid="stSidebar"] { background: #0b1727; }
div[data-testid="stMetric"] {
    background: #0e1b2d;
    border: 1px solid #26384e;
    padding: 14px;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    caminho = Path(__file__).parent / "partidas.csv"
    df = pd.read_csv(caminho)
    df["data_hora"] = pd.to_datetime(
        df["data"].astype(str) + " " + df["hora"].astype(str)
    )
    return df.sort_values("data_hora").reset_index(drop=True)

def criar_registros(df):
    registros = []
    for _, r in df.iterrows():
        j1_v = r["sets_j1"] > r["sets_j2"]
        registros.append({
            "id": r["id"],
            "data_hora": r["data_hora"],
            "dia_semana": r["dia_semana"],
            "jogador": r["jogador_1"],
            "adversario": r["jogador_2"],
            "sets_pro": int(r["sets_j1"]),
            "sets_contra": int(r["sets_j2"]),
            "resultado": "Vitória" if j1_v else "Derrota",
            "total_sets": int(r["sets_j1"] + r["sets_j2"]),
        })
        registros.append({
            "id": r["id"],
            "data_hora": r["data_hora"],
            "dia_semana": r["dia_semana"],
            "jogador": r["jogador_2"],
            "adversario": r["jogador_1"],
            "sets_pro": int(r["sets_j2"]),
            "sets_contra": int(r["sets_j1"]),
            "resultado": "Vitória" if not j1_v else "Derrota",
            "total_sets": int(r["sets_j1"] + r["sets_j2"]),
        })
    return pd.DataFrame(registros).sort_values("data_hora").reset_index(drop=True)

def calcular_sequencias(resultados):
    maior_v = maior_d = atual_v = atual_d = 0
    for resultado in resultados:
        if resultado == "Vitória":
            atual_v += 1
            atual_d = 0
        else:
            atual_d += 1
            atual_v = 0
        maior_v = max(maior_v, atual_v)
        maior_d = max(maior_d, atual_d)

    if not resultados:
        return 0, 0, "—"

    ultimo = resultados[-1]
    atual = 0
    for resultado in reversed(resultados):
        if resultado == ultimo:
            atual += 1
        else:
            break
    return maior_v, maior_d, f"{ultimo} ({atual})"

df = carregar_dados()
reg = criar_registros(df)
jogadores = sorted(reg["jogador"].unique().tolist())

st.title("🏓 Painel de Tênis de Mesa")
st.caption("Versão de teste com pesquisa, perfil, histórico e comparação de jogadores.")

pagina = st.sidebar.radio(
    "Navegação",
    ["Pesquisar jogador", "Comparar jogadores", "Histórico geral"]
)

if pagina == "Pesquisar jogador":
    st.subheader("Pesquisar jogador")
    termo = st.text_input(
        "Digite parte do nome",
        placeholder="Ex.: Mateusz, Kosmal ou Gajda"
    )

    encontrados = [
        nome for nome in jogadores
        if termo.strip().lower() in nome.lower()
    ] if termo.strip() else jogadores

    if not encontrados:
        st.warning("Nenhum jogador encontrado.")
        st.stop()

    jogador = st.selectbox("Selecione o jogador", encontrados)
    dados = reg[reg["jogador"] == jogador].sort_values("data_hora")

    jogos = len(dados)
    vitorias = int((dados["resultado"] == "Vitória").sum())
    derrotas = jogos - vitorias
    aproveitamento = (vitorias / jogos * 100) if jogos else 0
    maior_v, maior_d, sequencia_atual = calcular_sequencias(
        dados["resultado"].tolist()
    )

    intervalos = dados["data_hora"].diff().dt.total_seconds().div(60).dropna()
    intervalo_medio = intervalos.mean() if not intervalos.empty else None

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Jogos", jogos)
    c2.metric("Vitórias", vitorias)
    c3.metric("Derrotas", derrotas)
    c4.metric("Aproveitamento", f"{aproveitamento:.1f}%")

    st.markdown(f"### {jogador}")
    a, b = st.columns(2)
    with a:
        st.write(f"**Sequência atual:** {sequencia_atual}")
        st.write(f"**Maior sequência de vitórias:** {maior_v}")
        st.write(f"**Maior sequência de derrotas:** {maior_d}")
        st.write(
            "**Intervalo médio:** "
            + (f"{intervalo_medio:.1f} minutos" if intervalo_medio is not None else "—")
        )
        st.write(
            f"**Jogos em 3 / 4 / 5 sets:** "
            f"{int((dados['total_sets']==3).sum())} / "
            f"{int((dados['total_sets']==4).sum())} / "
            f"{int((dados['total_sets']==5).sum())}"
        )

    with b:
        faixas = pd.cut(
            dados["data_hora"].dt.hour,
            bins=[-1,2,5,8,11,14,17,20,23],
            labels=["00–03","03–06","06–09","09–12","12–15","15–18","18–21","21–24"]
        ).value_counts().sort_index()
        st.write("**Jogos por horário**")
        st.bar_chart(faixas)

    st.write("### Histórico do jogador")
    historico = dados.sort_values("data_hora", ascending=False).copy()
    historico["Data"] = historico["data_hora"].dt.strftime("%d/%m/%Y")
    historico["Hora"] = historico["data_hora"].dt.strftime("%H:%M")
    historico["Placar"] = (
        historico["sets_pro"].astype(str)
        + " x "
        + historico["sets_contra"].astype(str)
    )
    st.dataframe(
        historico[["Data","Hora","adversario","Placar","resultado"]]
        .rename(columns={
            "adversario":"Adversário",
            "resultado":"Resultado"
        }),
        use_container_width=True,
        hide_index=True
    )

elif pagina == "Comparar jogadores":
    st.subheader("Comparar jogadores")
    a, b = st.columns(2)
    jogador_a = a.selectbox("Jogador A", jogadores, index=0)
    jogador_b = b.selectbox(
        "Jogador B",
        jogadores,
        index=1 if len(jogadores) > 1 else 0
    )

    confrontos = df[
        ((df["jogador_1"] == jogador_a) & (df["jogador_2"] == jogador_b))
        | ((df["jogador_1"] == jogador_b) & (df["jogador_2"] == jogador_a))
    ].copy()

    if confrontos.empty:
        st.info("Nenhum confronto direto encontrado neste lote.")
    else:
        vencedor = confrontos.apply(
            lambda r: r["jogador_1"] if r["sets_j1"] > r["sets_j2"] else r["jogador_2"],
            axis=1
        )
        vit_a = int((vencedor == jogador_a).sum())
        vit_b = int((vencedor == jogador_b).sum())

        c1, c2, c3 = st.columns(3)
        c1.metric("Confrontos", len(confrontos))
        c2.metric(f"Vitórias — {jogador_a}", vit_a)
        c3.metric(f"Vitórias — {jogador_b}", vit_b)

        confrontos["Data"] = confrontos["data_hora"].dt.strftime("%d/%m/%Y")
        confrontos["Hora"] = confrontos["data_hora"].dt.strftime("%H:%M")
        confrontos["Placar"] = (
            confrontos["sets_j1"].astype(str)
            + " x "
            + confrontos["sets_j2"].astype(str)
        )
        st.dataframe(
            confrontos[
                ["Data","Hora","jogador_1","jogador_2","Placar"]
            ].rename(columns={
                "jogador_1":"Jogador 1",
                "jogador_2":"Jogador 2"
            }),
            use_container_width=True,
            hide_index=True
        )

else:
    st.subheader("Histórico geral")
    geral = df.sort_values("data_hora", ascending=False).copy()
    geral["Data"] = geral["data_hora"].dt.strftime("%d/%m/%Y")
    geral["Hora"] = geral["data_hora"].dt.strftime("%H:%M")
    geral["Placar"] = (
        geral["sets_j1"].astype(str)
        + " x "
        + geral["sets_j2"].astype(str)
    )
    st.dataframe(
        geral[
            ["id","Data","Hora","jogador_1","jogador_2","Placar"]
        ].rename(columns={
            "id":"ID",
            "jogador_1":"Jogador 1",
            "jogador_2":"Jogador 2"
        }),
        use_container_width=True,
        hide_index=True
    )
