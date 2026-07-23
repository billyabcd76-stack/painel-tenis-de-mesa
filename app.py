import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Match Intelligence",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent

st.markdown("""
<style>
:root {
    --bg:#F3F6FA;
    --panel:#FFFFFF;
    --line:#E5EAF0;
    --text:#101828;
    --muted:#667085;
    --green:#16A34A;
    --red:#DC2626;
    --blue:#2563EB;
    --amber:#D97706;
    --navy:#0B1220;
}
.stApp {background:var(--bg);}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0B1220 0%,#121B2D 100%);
}
[data-testid="stSidebar"] * {color:#F8FAFC;}
.block-container {padding-top:1.4rem; padding-bottom:2rem;}
h1,h2,h3 {color:var(--text);}
.hero {
    background:linear-gradient(135deg,#0B1220,#1E293B);
    border-radius:20px;
    padding:24px 28px;
    color:white;
    margin-bottom:18px;
}
.hero h1 {color:white;margin:0;font-size:2rem;}
.hero p {color:#CBD5E1;margin:.35rem 0 0;}
.card {
    background:var(--panel);
    border:1px solid var(--line);
    border-radius:18px;
    padding:18px;
    box-shadow:0 8px 24px rgba(16,24,40,.05);
}
.kpi-label {font-size:.78rem;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.04em;}
.kpi-value {font-size:1.65rem;color:var(--text);font-weight:800;margin-top:4px;}
.kpi-sub {font-size:.78rem;color:#98A2B3;margin-top:4px;}
.section {
    font-size:1.15rem;
    font-weight:800;
    color:var(--text);
    margin:18px 0 10px;
}
.badge-win {
    display:inline-block;background:#DCFCE7;color:#166534;padding:4px 9px;
    border-radius:999px;font-size:.78rem;font-weight:800;
}
.badge-loss {
    display:inline-block;background:#FEE2E2;color:#991B1B;padding:4px 9px;
    border-radius:999px;font-size:.78rem;font-weight:800;
}
.insight {
    background:#FFFFFF;border-left:5px solid #2563EB;border-radius:12px;
    padding:14px 16px;margin-bottom:10px;border-top:1px solid var(--line);
    border-right:1px solid var(--line);border-bottom:1px solid var(--line);
}
.insight strong {color:var(--text);}
.small {font-size:.84rem;color:var(--muted);}
div[data-baseweb="select"]>div {
    background:white;border-radius:12px;border-color:#D0D5DD;
}
[data-testid="stMetric"] {
    background:white;border:1px solid var(--line);padding:14px 16px;
    border-radius:16px;box-shadow:0 6px 18px rgba(16,24,40,.04);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    p = pd.read_csv(BASE / "partidas.csv")
    s = pd.read_csv(BASE / "sets.csv")
    j = pd.read_csv(BASE / "jogadores.csv")
    p["Data"] = pd.to_datetime(p["Data"], dayfirst=True, errors="coerce")
    s["Data"] = pd.to_datetime(s["Data"], dayfirst=True, errors="coerce")
    for c in ["Sets J1","Sets J2","Qtd. Sets","Total Pontos","Pontos J1","Pontos J2","Margem J1","Ordem Entrada"]:
        p[c] = pd.to_numeric(p[c], errors="coerce")
    for c in ["Nº Set","Pontos J1","Pontos J2","Diferença J1","Total Set"]:
        s[c] = pd.to_numeric(s[c], errors="coerce")
    return p,s,j

partidas, sets, jogadores = load_data()
nomes = sorted(set(partidas["Jogador 1"].dropna()) | set(partidas["Jogador 2"].dropna()))

def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def card(label, value, subtitle=""):
    st.markdown(
        f'<div class="card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-sub">{subtitle}</div></div>',
        unsafe_allow_html=True
    )

def player_matches(name):
    df = partidas[(partidas["Jogador 1"]==name)|(partidas["Jogador 2"]==name)].copy()
    if df.empty: return df
    df["Adversário"] = df.apply(lambda r: r["Jogador 2"] if r["Jogador 1"]==name else r["Jogador 1"], axis=1)
    df["Posição"] = df["Jogador 1"].apply(lambda x: "J1" if x==name else "J2")
    df["Sets Feitos"] = df.apply(lambda r: r["Sets J1"] if r["Jogador 1"]==name else r["Sets J2"], axis=1)
    df["Sets Sofridos"] = df.apply(lambda r: r["Sets J2"] if r["Jogador 1"]==name else r["Sets J1"], axis=1)
    df["Pontos Feitos"] = df.apply(lambda r: r["Pontos J1"] if r["Jogador 1"]==name else r["Pontos J2"], axis=1)
    df["Pontos Sofridos"] = df.apply(lambda r: r["Pontos J2"] if r["Jogador 1"]==name else r["Pontos J1"], axis=1)
    df["Resultado"] = df["Vencedor"].eq(name).map({True:"Vitória",False:"Derrota"})
    df["Placar"] = df["Sets Feitos"].astype(int).astype(str)+"×"+df["Sets Sofridos"].astype(int).astype(str)
    return df.sort_values(["Data","Horário","Ordem Entrada"], ascending=[True,True,True])

def player_sets(name):
    df = sets[(sets["Jogador 1"]==name)|(sets["Jogador 2"]==name)].copy()
    if df.empty: return df
    df["Pontos Feitos"] = df.apply(lambda r: r["Pontos J1"] if r["Jogador 1"]==name else r["Pontos J2"], axis=1)
    df["Pontos Sofridos"] = df.apply(lambda r: r["Pontos J2"] if r["Jogador 1"]==name else r["Pontos J1"], axis=1)
    df["Venceu"] = df["Vencedor Set"].eq(name)
    return df

def streaks(results):
    current_type = None
    current = 0
    max_w = 0
    max_l = 0
    for r in results:
        t = "V" if r=="Vitória" else "D"
        if t == current_type:
            current += 1
        else:
            current_type = t
            current = 1
        if t=="V": max_w=max(max_w,current)
        else: max_l=max(max_l,current)
    return current_type, current, max_w, max_l

def scoreline_counts(df):
    wins = df[df["Resultado"]=="Vitória"]["Placar"].value_counts()
    losses = df[df["Resultado"]=="Derrota"]["Placar"].value_counts()
    rows=[]
    for placar in ["3×0","3×1","3×2"]:
        rows.append({"Tipo":"Vitória","Placar":placar,"Quantidade":int(wins.get(placar,0))})
    for placar in ["0×3","1×3","2×3"]:
        rows.append({"Tipo":"Derrota","Placar":placar,"Quantidade":int(losses.get(placar,0))})
    return pd.DataFrame(rows)

def first_set_effect(name):
    pm = player_matches(name)
    ps = player_sets(name)
    if pm.empty or ps.empty: return {}
    fs = ps[ps["Nº Set"]==1][["ID Partida","Venceu"]].copy()
    merged = pm.merge(fs, left_on="ID Partida", right_on="ID Partida", how="left")
    won_first = merged[merged["Venceu"]==True]
    lost_first = merged[merged["Venceu"]==False]
    return {
        "won_first_n": len(won_first),
        "won_first_match_wins": int((won_first["Resultado"]=="Vitória").sum()),
        "lost_first_n": len(lost_first),
        "lost_first_match_wins": int((lost_first["Resultado"]=="Vitória").sum()),
    }

def h2h(a,b):
    return partidas[
        ((partidas["Jogador 1"]==a)&(partidas["Jogador 2"]==b)) |
        ((partidas["Jogador 1"]==b)&(partidas["Jogador 2"]==a))
    ].copy().sort_values(["Data","Horário","Ordem Entrada"], ascending=False)

st.sidebar.markdown("## MATCH INTELLIGENCE")
st.sidebar.caption("Painel de padrões e desempenho")
page = st.sidebar.radio(
    "",
    ["Central de Análise","Comparador H2H","Histórico Geral","Jogos por Data","Base"],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")
st.sidebar.info(f"{len(partidas)} partidas oficiais\n\n{len(sets)} sets registrados")

if page == "Central de Análise":
    hero("Central de Análise", "Encontre padrões de forma, sequência, placares e comportamento por set.")
    name = st.selectbox("Pesquisar jogador", nomes, key="central_player")
    pm = player_matches(name)
    ps = player_sets(name)
    vit = int((pm["Resultado"]=="Vitória").sum())
    cur_t, cur_n, max_w, max_l = streaks(pm["Resultado"].tolist())

    cols = st.columns(5)
    with cols[0]: card("Partidas", len(pm), "Histórico completo")
    with cols[1]: card("Vitórias", vit, f"{vit/len(pm):.1%} de aproveitamento")
    with cols[2]: card("Derrotas", len(pm)-vit, "Total de derrotas")
    with cols[3]: card("Sequência atual", f"{cur_n} {'vitórias' if cur_t=='V' else 'derrotas'}", "Forma mais recente")
    with cols[4]: card("Saldo médio", f"{(pm['Pontos Feitos']-pm['Pontos Sofridos']).mean():.1f}", "Pontos por partida")

    st.markdown('<div class="section">Padrões detectados</div>', unsafe_allow_html=True)
    fs = first_set_effect(name)
    by_set = ps.groupby("Nº Set").agg(
        Sets=("ID Set","count"),
        Vitórias=("Venceu","sum"),
        Média_feitos=("Pontos Feitos","mean"),
        Média_sofridos=("Pontos Sofridos","mean")
    ).reset_index()
    by_set["Aproveitamento"] = by_set["Vitórias"]/by_set["Sets"]
    by_set["Saldo"] = by_set["Média_feitos"]-by_set["Média_sofridos"]

    best = by_set.sort_values(["Aproveitamento","Saldo"],ascending=False).iloc[0]
    worst = by_set.sort_values(["Aproveitamento","Saldo"],ascending=True).iloc[0]

    insights = [
        f"<strong>Maior sequência positiva:</strong> {max_w} vitória(s) consecutiva(s).",
        f"<strong>Maior sequência negativa:</strong> {max_l} derrota(s) consecutiva(s).",
        f"<strong>Set mais forte:</strong> {int(best['Nº Set'])}º set, com {best['Aproveitamento']:.1%} de aproveitamento.",
        f"<strong>Set mais fraco:</strong> {int(worst['Nº Set'])}º set, com {worst['Aproveitamento']:.1%} de aproveitamento.",
    ]
    if fs:
        confirm = fs["won_first_match_wins"]/fs["won_first_n"] if fs["won_first_n"] else 0
        comeback = fs["lost_first_match_wins"]/fs["lost_first_n"] if fs["lost_first_n"] else 0
        insights += [
            f"<strong>Depois de vencer o 1º set:</strong> venceu a partida em {confirm:.1%} das vezes.",
            f"<strong>Depois de perder o 1º set:</strong> conseguiu virar em {comeback:.1%} das vezes.",
        ]
    for i in insights:
        st.markdown(f'<div class="insight">{i}</div>', unsafe_allow_html=True)

    t1,t2,t3,t4,t5 = st.tabs([
        "Sequência recente","Força por set","Placares","Adversários","Histórico completo"
    ])

    with t1:
        recent = pm.sort_values(["Data","Horário","Ordem Entrada"],ascending=False).head(10).copy()
        recent["Data"] = recent["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(
            recent[["Data","Horário","Adversário","Posição","Placar","Resultado","Pontos Feitos","Pontos Sofridos"]],
            use_container_width=True, hide_index=True
        )
        form = recent.sort_values(["Data","Horário"]).set_index("Data")["Resultado"].map({"Vitória":1,"Derrota":0})
        st.caption("1 = vitória | 0 = derrota")
        st.line_chart(form)

    with t2:
        st.dataframe(
            by_set[["Nº Set","Sets","Vitórias","Aproveitamento","Média_feitos","Média_sofridos","Saldo"]]
            .style.format({
                "Aproveitamento":"{:.1%}",
                "Média_feitos":"{:.1f}",
                "Média_sofridos":"{:.1f}",
                "Saldo":"{:.1f}"
            }),
            use_container_width=True, hide_index=True
        )
        st.bar_chart(by_set.set_index("Nº Set")[["Aproveitamento"]])

    with t3:
        sc = scoreline_counts(pm)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Vitórias por placar**")
            st.dataframe(sc[sc["Tipo"]=="Vitória"],use_container_width=True,hide_index=True)
        with c2:
            st.markdown("**Derrotas por placar**")
            st.dataframe(sc[sc["Tipo"]=="Derrota"],use_container_width=True,hide_index=True)

    with t4:
        adv = pm.groupby("Adversário").agg(
            Partidas=("Resultado","size"),
            Vitórias=("Resultado",lambda x:(x=="Vitória").sum()),
            Média_feitos=("Pontos Feitos","mean"),
            Média_sofridos=("Pontos Sofridos","mean")
        ).reset_index()
        adv["Derrotas"] = adv["Partidas"]-adv["Vitórias"]
        adv["Aproveitamento"] = adv["Vitórias"]/adv["Partidas"]
        adv["Saldo"] = adv["Média_feitos"]-adv["Média_sofridos"]
        st.dataframe(
            adv.sort_values(["Partidas","Aproveitamento"],ascending=False)
            .style.format({
                "Aproveitamento":"{:.1%}",
                "Média_feitos":"{:.1f}",
                "Média_sofridos":"{:.1f}",
                "Saldo":"{:.1f}"
            }),
            use_container_width=True, hide_index=True
        )

    with t5:
        hist = pm.sort_values(["Data","Horário","Ordem Entrada"],ascending=False).copy()
        hist["Data"] = hist["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(
            hist[["Data","Horário","Adversário","Posição","Placar","Resultado","Pontos Feitos","Pontos Sofridos","Total Pontos"]],
            use_container_width=True, hide_index=True
        )

elif page == "Comparador H2H":
    hero("Comparador H2H", "Compare dois jogadores, veja o histórico completo e os padrões por set.")
    c1,c2 = st.columns(2)
    a = c1.selectbox("Jogador A", nomes, index=0)
    b = c2.selectbox("Jogador B", [x for x in nomes if x!=a], index=0)
    df = h2h(a,b)

    if df.empty:
        st.warning("Não há confrontos registrados entre esses jogadores.")
    else:
        va = int((df["Vencedor"]==a).sum())
        vb = int((df["Vencedor"]==b).sum())
        ca,cb,cc,cd = st.columns(4)
        with ca: card("Confrontos",len(df),"Histórico completo")
        with cb: card(f"Vitórias {a}",va,f"{va/len(df):.1%}")
        with cc: card(f"Vitórias {b}",vb,f"{vb/len(df):.1%}")
        with cd: card("Média de pontos",f"{df['Total Pontos'].mean():.1f}","Por confronto")

        df["Sets A"] = df.apply(lambda r:r["Sets J1"] if r["Jogador 1"]==a else r["Sets J2"],axis=1)
        df["Sets B"] = df.apply(lambda r:r["Sets J2"] if r["Jogador 1"]==a else r["Sets J1"],axis=1)
        df["Pontos A"] = df.apply(lambda r:r["Pontos J1"] if r["Jogador 1"]==a else r["Pontos J2"],axis=1)
        df["Pontos B"] = df.apply(lambda r:r["Pontos J2"] if r["Jogador 1"]==a else r["Pontos J1"],axis=1)
        df["Placar A"] = df["Sets A"].astype(int).astype(str)+"×"+df["Sets B"].astype(int).astype(str)

        tabs = st.tabs(["Histórico","Padrões por set","Placares","Posição"])
        with tabs[0]:
            hist = df.copy()
            hist["Data"] = hist["Data"].dt.strftime("%d/%m/%Y")
            st.dataframe(
                hist[["Data","Horário","Jogador 1","Jogador 2","Placar A","Vencedor","Pontos A","Pontos B","Total Pontos"]],
                use_container_width=True, hide_index=True
            )
        with tabs[1]:
            hs = sets[
                ((sets["Jogador 1"]==a)&(sets["Jogador 2"]==b)) |
                ((sets["Jogador 1"]==b)&(sets["Jogador 2"]==a))
            ].copy()
            hs["Pontos A"] = hs.apply(lambda r:r["Pontos J1"] if r["Jogador 1"]==a else r["Pontos J2"],axis=1)
            hs["Pontos B"] = hs.apply(lambda r:r["Pontos J2"] if r["Jogador 1"]==a else r["Pontos J1"],axis=1)
            hs["Venceu A"] = hs["Vencedor Set"].eq(a)
            bs = hs.groupby("Nº Set").agg(
                Disputados=("ID Set","count"),
                Vitórias_A=("Venceu A","sum"),
                Média_A=("Pontos A","mean"),
                Média_B=("Pontos B","mean")
            ).reset_index()
            bs["Vitórias_B"]=bs["Disputados"]-bs["Vitórias_A"]
            bs["Aproveitamento_A"]=bs["Vitórias_A"]/bs["Disputados"]
            st.dataframe(
                bs.style.format({
                    "Aproveitamento_A":"{:.1%}",
                    "Média_A":"{:.1f}",
                    "Média_B":"{:.1f}"
                }),
                use_container_width=True,hide_index=True
            )
        with tabs[2]:
            st.dataframe(df["Placar A"].value_counts().rename_axis("Placar").reset_index(name="Quantidade"),
                         use_container_width=True,hide_index=True)
        with tabs[3]:
            rows=[]
            for n in [a,b]:
                for pos,col in [("J1","Jogador 1"),("J2","Jogador 2")]:
                    sub=df[df[col]==n]
                    rows.append({
                        "Jogador":n,"Posição":pos,"Partidas":len(sub),
                        "Vitórias":int((sub["Vencedor"]==n).sum())
                    })
            pos=pd.DataFrame(rows)
            pos["Aproveitamento"]=pos.apply(lambda r:0 if r["Partidas"]==0 else r["Vitórias"]/r["Partidas"],axis=1)
            st.dataframe(pos.style.format({"Aproveitamento":"{:.1%}"}),use_container_width=True,hide_index=True)

elif page == "Histórico Geral":
    hero("Histórico Geral","Consulte todas as partidas de qualquer jogador.")
    jogador = st.selectbox("Pesquisar jogador", ["Todos"]+nomes)
    df = partidas.copy()
    if jogador!="Todos":
        df=df[(df["Jogador 1"]==jogador)|(df["Jogador 2"]==jogador)]
    df=df.sort_values(["Data","Horário","Ordem Entrada"],ascending=False)
    df["Data"]=df["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df,use_container_width=True,hide_index=True)

elif page == "Jogos por Data":
    hero("Jogos por Data","Veja a sequência completa de partidas em cada dia.")
    dates=sorted(partidas["Data"].dropna().dt.date.unique(),reverse=True)
    d=st.selectbox("Data",dates)
    df=partidas[partidas["Data"].dt.date==d].sort_values(["Horário","Ordem Entrada"])
    st.dataframe(
        df[["Horário","Jogador 1","Jogador 2","Sets J1","Sets J2","Vencedor","Total Pontos","Qtd. Sets"]],
        use_container_width=True,hide_index=True
    )

elif page == "Base":
    hero("Base de Dados","Base oficial atual, sem as 102 partidas antigas.")
    t1,t2=st.tabs(["Partidas","Sets"])
    with t1: st.dataframe(partidas,use_container_width=True,hide_index=True)
    with t2: st.dataframe(sets,use_container_width=True,hide_index=True)
