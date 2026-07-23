import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Painel Pro — Tênis de Mesa",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent

st.markdown("""
<style>
    .stApp {background: #F5F7FB;}
    [data-testid="stSidebar"] {background: #0F172A;}
    [data-testid="stSidebar"] * {color: #F8FAFC;}
    .main-title {
        font-size: 2rem; font-weight: 800; color: #0F172A; margin-bottom: 0;
    }
    .sub-title {
        color: #64748B; margin-top: .2rem; margin-bottom: 1.2rem;
    }
    .card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 18px rgba(15,23,42,.05);
        margin-bottom: 12px;
    }
    .metric-label {color:#64748B; font-size:.85rem; font-weight:600;}
    .metric-value {color:#0F172A; font-size:1.65rem; font-weight:800; line-height:1.2;}
    .win {color:#15803D; font-weight:800;}
    .loss {color:#B91C1C; font-weight:800;}
    .neutral {color:#334155; font-weight:700;}
    .section-title {font-size:1.2rem; font-weight:800; color:#0F172A; margin-top:1rem;}
    div[data-baseweb="select"] > div {
        background: white;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    partidas = pd.read_csv(BASE / "partidas.csv")
    sets = pd.read_csv(BASE / "sets.csv")
    jogadores = pd.read_csv(BASE / "jogadores.csv")

    partidas["Data"] = pd.to_datetime(partidas["Data"], dayfirst=True, errors="coerce")
    sets["Data"] = pd.to_datetime(sets["Data"], dayfirst=True, errors="coerce")

    for c in ["Sets J1","Sets J2","Qtd. Sets","Total Pontos","Pontos J1","Pontos J2","Margem J1"]:
        partidas[c] = pd.to_numeric(partidas[c], errors="coerce")

    for c in ["Nº Set","Pontos J1","Pontos J2","Diferença J1","Total Set"]:
        sets[c] = pd.to_numeric(sets[c], errors="coerce")

    return partidas, sets, jogadores

partidas, sets, jogadores = carregar_dados()
nomes = sorted(set(partidas["Jogador 1"].dropna()) | set(partidas["Jogador 2"].dropna()))

def metric_card(label, value, subtitle=None):
    sub = f'<div style="color:#94A3B8;font-size:.78rem;margin-top:4px">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>{sub}</div>',
        unsafe_allow_html=True
    )

def jogos_do_jogador(nome):
    df = partidas[(partidas["Jogador 1"] == nome) | (partidas["Jogador 2"] == nome)].copy()
    if df.empty:
        return df
    df["Adversário"] = df.apply(lambda r: r["Jogador 2"] if r["Jogador 1"] == nome else r["Jogador 1"], axis=1)
    df["Posição"] = df["Jogador 1"].apply(lambda x: "J1" if x == nome else "J2")
    df["Pontos Feitos"] = df.apply(lambda r: r["Pontos J1"] if r["Jogador 1"] == nome else r["Pontos J2"], axis=1)
    df["Pontos Sofridos"] = df.apply(lambda r: r["Pontos J2"] if r["Jogador 1"] == nome else r["Pontos J1"], axis=1)
    df["Sets Feitos"] = df.apply(lambda r: r["Sets J1"] if r["Jogador 1"] == nome else r["Sets J2"], axis=1)
    df["Sets Sofridos"] = df.apply(lambda r: r["Sets J2"] if r["Jogador 1"] == nome else r["Sets J1"], axis=1)
    df["Resultado"] = df["Vencedor"].apply(lambda x: "Vitória" if x == nome else "Derrota")
    df["Placar"] = df["Sets Feitos"].astype(int).astype(str) + " × " + df["Sets Sofridos"].astype(int).astype(str)
    return df.sort_values(["Data","Horário"], ascending=False)

def h2h_df(a, b):
    return partidas[
        ((partidas["Jogador 1"] == a) & (partidas["Jogador 2"] == b)) |
        ((partidas["Jogador 1"] == b) & (partidas["Jogador 2"] == a))
    ].copy().sort_values(["Data","Horário"], ascending=False)

def sets_h2h(a, b):
    return sets[
        ((sets["Jogador 1"] == a) & (sets["Jogador 2"] == b)) |
        ((sets["Jogador 1"] == b) & (sets["Jogador 2"] == a))
    ].copy()

def pct(v, total):
    return 0 if total == 0 else v / total

st.sidebar.markdown("## 🏓 PAINEL PRO")
st.sidebar.caption("Análise rápida e profissional")
pagina = st.sidebar.radio(
    "Menu",
    ["Visão Geral", "Comparar Duelo", "Análise de Jogador", "Jogos do Dia", "Base Completa"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.success(f"Base ativa: {len(partidas)} partidas")
st.sidebar.caption("As 102 partidas antigas não são consideradas.")

if pagina == "Visão Geral":
    st.markdown('<div class="main-title">Visão Geral</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Resumo da base oficial e principais padrões.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Partidas", len(partidas), "Base oficial")
    with c2: metric_card("Sets", len(sets), "Registrados set por set")
    with c3: metric_card("Jogadores", len(nomes), "Jogadores únicos")
    with c4: metric_card("Média de pontos", f'{partidas["Total Pontos"].mean():.1f}', "Por partida")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown('<div class="section-title">Ranking atual</div>', unsafe_allow_html=True)
        ranking = []
        for n in nomes:
            j = jogos_do_jogador(n)
            vit = (j["Resultado"] == "Vitória").sum()
            ranking.append({
                "Jogador": n,
                "J": len(j),
                "V": vit,
                "D": len(j)-vit,
                "Aproveitamento": pct(vit, len(j)),
                "Saldo médio": (j["Pontos Feitos"]-j["Pontos Sofridos"]).mean()
            })
        ranking = pd.DataFrame(ranking).sort_values(["Aproveitamento","J"], ascending=False)
        st.dataframe(
            ranking.style.format({"Aproveitamento":"{:.1%}","Saldo médio":"{:.1f}"}),
            use_container_width=True, hide_index=True, height=420
        )
    with right:
        st.markdown('<div class="section-title">Partidas por duração</div>', unsafe_allow_html=True)
        dist = partidas["Qtd. Sets"].value_counts().sort_index()
        st.bar_chart(dist)
        st.markdown('<div class="section-title">Média de pontos por set</div>', unsafe_allow_html=True)
        mp = sets.groupby("Nº Set")["Total Set"].mean()
        st.line_chart(mp)

elif pagina == "Comparar Duelo":
    st.markdown('<div class="main-title">Comparar Duelo</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Pesquise dois jogadores e veja todo o histórico entre eles.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        jogador_a = st.selectbox("Pesquisar Jogador A", nomes, index=0, key="duelo_a")
    with c2:
        candidatos = [n for n in nomes if n != jogador_a]
        jogador_b = st.selectbox("Pesquisar Jogador B", candidatos, index=0, key="duelo_b")

    duelo = h2h_df(jogador_a, jogador_b)
    duelo_sets = sets_h2h(jogador_a, jogador_b)

    if duelo.empty:
        st.warning("Não existe confronto entre esses jogadores na base atual.")
    else:
        va = int((duelo["Vencedor"] == jogador_a).sum())
        vb = int((duelo["Vencedor"] == jogador_b).sum())

        duelo["Pontos A"] = duelo.apply(lambda r: r["Pontos J1"] if r["Jogador 1"] == jogador_a else r["Pontos J2"], axis=1)
        duelo["Pontos B"] = duelo.apply(lambda r: r["Pontos J2"] if r["Jogador 1"] == jogador_a else r["Pontos J1"], axis=1)
        duelo["Sets A"] = duelo.apply(lambda r: r["Sets J1"] if r["Jogador 1"] == jogador_a else r["Sets J2"], axis=1)
        duelo["Sets B"] = duelo.apply(lambda r: r["Sets J2"] if r["Jogador 1"] == jogador_a else r["Sets J1"], axis=1)
        duelo["Placar"] = duelo["Sets A"].astype(int).astype(str) + " × " + duelo["Sets B"].astype(int).astype(str)
        duelo["Vencedor curto"] = duelo["Vencedor"]

        m1,m2,m3,m4 = st.columns(4)
        with m1: metric_card("Confrontos", len(duelo))
        with m2: metric_card(f"Vitórias · {jogador_a}", va, f"{pct(va,len(duelo)):.1%}")
        with m3: metric_card(f"Vitórias · {jogador_b}", vb, f"{pct(vb,len(duelo)):.1%}")
        with m4: metric_card("Média total", f'{duelo["Total Pontos"].mean():.1f}', "Pontos por partida")

        st.markdown('<div class="section-title">Histórico completo dos duelos</div>', unsafe_allow_html=True)
        hist = duelo[["Data","Horário","Jogador 1","Jogador 2","Placar","Vencedor curto","Total Pontos","Qtd. Sets"]].copy()
        hist["Data"] = hist["Data"].dt.strftime("%d/%m/%Y")
        hist.columns = ["Data","Horário","Jogador 1","Jogador 2","Placar","Vencedor","Pontos","Sets"]
        st.dataframe(hist, use_container_width=True, hide_index=True)

        t1,t2,t3 = st.tabs(["Resumo do confronto", "Desempenho por set", "Posição J1/J2"])
        with t1:
            r1,r2,r3 = st.columns(3)
            with r1: metric_card(f"Média de pontos · {jogador_a}", f'{duelo["Pontos A"].mean():.1f}')
            with r2: metric_card(f"Média de pontos · {jogador_b}", f'{duelo["Pontos B"].mean():.1f}')
            with r3: metric_card("Média de sets", f'{duelo["Qtd. Sets"].mean():.1f}')

            resultados = duelo["Placar"].value_counts().rename_axis("Placar").reset_index(name="Ocorrências")
            st.dataframe(resultados, use_container_width=True, hide_index=True)

        with t2:
            duelo_sets["Pontos A"] = duelo_sets.apply(
                lambda r: r["Pontos J1"] if r["Jogador 1"] == jogador_a else r["Pontos J2"], axis=1
            )
            duelo_sets["Pontos B"] = duelo_sets.apply(
                lambda r: r["Pontos J2"] if r["Jogador 1"] == jogador_a else r["Pontos J1"], axis=1
            )
            duelo_sets["Venceu A"] = duelo_sets["Vencedor Set"] == jogador_a
            por_set = duelo_sets.groupby("Nº Set").agg(
                Disputados=("ID Set","count"),
                Vitórias_A=("Venceu A","sum"),
                Média_A=("Pontos A","mean"),
                Média_B=("Pontos B","mean"),
                Média_total=("Total Set","mean")
            ).reset_index()
            por_set["Vitórias_B"] = por_set["Disputados"] - por_set["Vitórias_A"]
            por_set["Aproveitamento_A"] = por_set["Vitórias_A"] / por_set["Disputados"]
            st.dataframe(
                por_set[["Nº Set","Disputados","Vitórias_A","Vitórias_B","Aproveitamento_A","Média_A","Média_B","Média_total"]]
                .style.format({
                    "Aproveitamento_A":"{:.1%}","Média_A":"{:.1f}",
                    "Média_B":"{:.1f}","Média_total":"{:.1f}"
                }),
                use_container_width=True, hide_index=True
            )

        with t3:
            pos = []
            for nome in [jogador_a, jogador_b]:
                como_j1 = duelo[duelo["Jogador 1"] == nome]
                como_j2 = duelo[duelo["Jogador 2"] == nome]
                pos.extend([
                    {"Jogador":nome,"Posição":"J1","Partidas":len(como_j1),"Vitórias":int((como_j1["Vencedor"]==nome).sum())},
                    {"Jogador":nome,"Posição":"J2","Partidas":len(como_j2),"Vitórias":int((como_j2["Vencedor"]==nome).sum())},
                ])
            pos = pd.DataFrame(pos)
            pos["Aproveitamento"] = pos.apply(lambda r: pct(r["Vitórias"],r["Partidas"]),axis=1)
            st.dataframe(pos.style.format({"Aproveitamento":"{:.1%}"}), use_container_width=True, hide_index=True)

elif pagina == "Análise de Jogador":
    st.markdown('<div class="main-title">Análise de Jogador</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Pesquise um jogador e analise histórico, forma e desempenho por set.</div>', unsafe_allow_html=True)

    nome = st.selectbox("Pesquisar jogador", nomes, key="individual")
    jogos = jogos_do_jogador(nome)
    vit = int((jogos["Resultado"] == "Vitória").sum())

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: metric_card("Partidas", len(jogos))
    with c2: metric_card("Vitórias", vit)
    with c3: metric_card("Derrotas", len(jogos)-vit)
    with c4: metric_card("Aproveitamento", f"{pct(vit,len(jogos)):.1%}")
    with c5: metric_card("Saldo médio", f'{(jogos["Pontos Feitos"]-jogos["Pontos Sofridos"]).mean():.1f}')

    tab1,tab2,tab3,tab4 = st.tabs(["Histórico", "Por set", "Por adversário", "Por posição"])
    with tab1:
        historico = jogos[["Data","Horário","Posição","Adversário","Placar","Resultado","Pontos Feitos","Pontos Sofridos","Total Pontos"]].copy()
        historico["Data"] = historico["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(historico, use_container_width=True, hide_index=True)

    with tab2:
        sj = sets[(sets["Jogador 1"] == nome) | (sets["Jogador 2"] == nome)].copy()
        sj["Pontos Feitos"] = sj.apply(lambda r: r["Pontos J1"] if r["Jogador 1"] == nome else r["Pontos J2"], axis=1)
        sj["Pontos Sofridos"] = sj.apply(lambda r: r["Pontos J2"] if r["Jogador 1"] == nome else r["Pontos J1"], axis=1)
        sj["Venceu"] = sj["Vencedor Set"] == nome
        ps = sj.groupby("Nº Set").agg(
            Disputados=("ID Set","count"),
            Vencidos=("Venceu","sum"),
            Média_feitos=("Pontos Feitos","mean"),
            Média_sofridos=("Pontos Sofridos","mean"),
        ).reset_index()
        ps["Aproveitamento"] = ps["Vencidos"]/ps["Disputados"]
        ps["Saldo"] = ps["Média_feitos"]-ps["Média_sofridos"]
        st.dataframe(
            ps.style.format({"Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}","Média_sofridos":"{:.1f}","Saldo":"{:.1f}"}),
            use_container_width=True, hide_index=True
        )

    with tab3:
        adv = jogos.groupby("Adversário").agg(
            Partidas=("Resultado","size"),
            Vitórias=("Resultado",lambda x:(x=="Vitória").sum()),
            Média_feitos=("Pontos Feitos","mean"),
            Média_sofridos=("Pontos Sofridos","mean")
        ).reset_index()
        adv["Derrotas"] = adv["Partidas"]-adv["Vitórias"]
        adv["Aproveitamento"] = adv["Vitórias"]/adv["Partidas"]
        adv = adv.sort_values(["Partidas","Aproveitamento"],ascending=False)
        st.dataframe(
            adv[["Adversário","Partidas","Vitórias","Derrotas","Aproveitamento","Média_feitos","Média_sofridos"]]
            .style.format({"Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}","Média_sofridos":"{:.1f}"}),
            use_container_width=True, hide_index=True
        )

    with tab4:
        pos = jogos.groupby("Posição").agg(
            Partidas=("Resultado","size"),
            Vitórias=("Resultado",lambda x:(x=="Vitória").sum()),
            Média_feitos=("Pontos Feitos","mean"),
            Média_sofridos=("Pontos Sofridos","mean")
        ).reset_index()
        pos["Aproveitamento"] = pos["Vitórias"]/pos["Partidas"]
        st.dataframe(
            pos.style.format({"Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}","Média_sofridos":"{:.1f}"}),
            use_container_width=True, hide_index=True
        )

elif pagina == "Jogos do Dia":
    st.markdown('<div class="main-title">Jogos do Dia</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Filtre rapidamente por data e jogador.</div>', unsafe_allow_html=True)

    datas = sorted(partidas["Data"].dropna().dt.date.unique(), reverse=True)
    c1,c2 = st.columns(2)
    data = c1.selectbox("Data", datas)
    jogador = c2.selectbox("Jogador", ["Todos"] + nomes)

    df = partidas[partidas["Data"].dt.date == data].copy()
    if jogador != "Todos":
        df = df[(df["Jogador 1"]==jogador)|(df["Jogador 2"]==jogador)]
    df = df.sort_values(["Horário","Ordem Entrada"])

    metric_card("Partidas encontradas", len(df))
    st.dataframe(
        df[["Horário","Jogador 1","Jogador 2","Sets J1","Sets J2","Vencedor","Total Pontos","Qtd. Sets"]],
        use_container_width=True, hide_index=True
    )

elif pagina == "Base Completa":
    st.markdown('<div class="main-title">Base Completa</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Consulte todos os registros oficiais.</div>', unsafe_allow_html=True)
    t1,t2 = st.tabs(["Partidas","Sets"])
    with t1:
        st.dataframe(partidas, use_container_width=True, hide_index=True)
    with t2:
        st.dataframe(sets, use_container_width=True, hide_index=True)
