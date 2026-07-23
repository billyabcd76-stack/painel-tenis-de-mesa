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
:root{
  --bg:#08111F;
  --panel:#0F1B2D;
  --panel2:#132238;
  --line:#24364D;
  --text:#F8FAFC;
  --muted:#94A3B8;
  --blue:#2F80ED;
  --green:#27AE60;
  --red:#EB5757;
  --orange:#F2994A;
  --purple:#9B51E0;
  --cyan:#2D9CDB;
}
.stApp{background:linear-gradient(180deg,#07101C 0%,#0B1525 100%);}
.block-container{padding-top:1.2rem;padding-bottom:2rem;max-width:1600px;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#091524 0%,#0D1B2E 100%);
  border-right:1px solid #1B2B41;
}
[data-testid="stSidebar"] *{color:#EAF2FF;}
[data-testid="stSidebarNav"]{display:none;}
h1,h2,h3,h4,p,label,span{color:var(--text);}
div[data-testid="stMetric"]{
  background:linear-gradient(180deg,#122137,#0F1B2D);
  border:1px solid var(--line);
  padding:16px 18px;
  border-radius:14px;
  box-shadow:0 10px 25px rgba(0,0,0,.18);
}
div[data-testid="stMetricLabel"]{color:#A8B6C8;}
div[data-testid="stMetricValue"]{color:#FFFFFF;font-weight:800;}
div[data-baseweb="select"]>div{
  background:#0F1B2D!important;
  border:1px solid #31455E!important;
  border-radius:10px!important;
  color:#FFFFFF!important;
}
div[data-baseweb="input"] input{
  background:#0F1B2D!important;
  color:white!important;
}
[data-testid="stDataFrame"]{
  border:1px solid var(--line);
  border-radius:12px;
  overflow:hidden;
}
.hero{
  background:linear-gradient(135deg,#0D1B2E 0%,#132B49 100%);
  border:1px solid #254262;
  border-radius:18px;
  padding:20px 24px;
  margin-bottom:16px;
  box-shadow:0 14px 35px rgba(0,0,0,.22);
}
.hero h1{margin:0;color:#FFF;font-size:2rem;font-weight:850;}
.hero p{margin:.35rem 0 0;color:#A9BCD3;}
.panel{
  background:linear-gradient(180deg,#101D30 0%,#0E192A 100%);
  border:1px solid #263A53;
  border-radius:14px;
  padding:16px;
  min-height:100%;
  box-shadow:0 10px 24px rgba(0,0,0,.14);
}
.panel-title{
  color:#F8FAFC;
  font-weight:800;
  font-size:.95rem;
  text-transform:uppercase;
  margin-bottom:10px;
}
.small{color:#91A4BC;font-size:.82rem;}
.badge{
  display:inline-block;
  padding:4px 9px;
  border-radius:999px;
  font-size:.75rem;
  font-weight:800;
}
.win{background:#153B2A;color:#4ADE80;}
.loss{background:#3B1E25;color:#FB7185;}
.info{background:#16314A;color:#60A5FA;}
.insight{
  background:#0F1B2D;
  border:1px solid #263A53;
  border-left:4px solid #2F80ED;
  border-radius:10px;
  padding:12px 14px;
  margin-bottom:8px;
  color:#DDE7F5;
}
hr{border-color:#21354C;}
.stTabs [data-baseweb="tab-list"]{gap:8px;}
.stTabs [data-baseweb="tab"]{
  background:#0E192A;
  border:1px solid #263A53;
  border-radius:10px 10px 0 0;
  color:#AFC1D8;
}
.stTabs [aria-selected="true"]{
  background:#173454!important;
  color:white!important;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    p = pd.read_csv(BASE/"partidas.csv")
    s = pd.read_csv(BASE/"sets.csv")
    j = pd.read_csv(BASE/"jogadores.csv")

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

def player_matches(name):
    df = partidas[(partidas["Jogador 1"]==name)|(partidas["Jogador 2"]==name)].copy()
    if df.empty: return df
    df["Adversário"] = df.apply(lambda r:r["Jogador 2"] if r["Jogador 1"]==name else r["Jogador 1"],axis=1)
    df["Posição"] = df["Jogador 1"].apply(lambda x:"J1" if x==name else "J2")
    df["Sets Feitos"] = df.apply(lambda r:r["Sets J1"] if r["Jogador 1"]==name else r["Sets J2"],axis=1)
    df["Sets Sofridos"] = df.apply(lambda r:r["Sets J2"] if r["Jogador 1"]==name else r["Sets J1"],axis=1)
    df["Pontos Feitos"] = df.apply(lambda r:r["Pontos J1"] if r["Jogador 1"]==name else r["Pontos J2"],axis=1)
    df["Pontos Sofridos"] = df.apply(lambda r:r["Pontos J2"] if r["Jogador 1"]==name else r["Pontos J1"],axis=1)
    df["Resultado"] = df["Vencedor"].eq(name).map({True:"Vitória",False:"Derrota"})
    df["Placar"] = df["Sets Feitos"].astype(int).astype(str)+" × "+df["Sets Sofridos"].astype(int).astype(str)
    return df.sort_values(["Data","Horário","Ordem Entrada"])

def player_sets(name):
    df=sets[(sets["Jogador 1"]==name)|(sets["Jogador 2"]==name)].copy()
    if df.empty:return df
    df["Pontos Feitos"]=df.apply(lambda r:r["Pontos J1"] if r["Jogador 1"]==name else r["Pontos J2"],axis=1)
    df["Pontos Sofridos"]=df.apply(lambda r:r["Pontos J2"] if r["Jogador 1"]==name else r["Pontos J1"],axis=1)
    df["Venceu"]=df["Vencedor Set"].eq(name)
    return df

def streaks(results):
    current_type=None; current=0; max_w=0; max_l=0
    for r in results:
        t="V" if r=="Vitória" else "D"
        if t==current_type: current+=1
        else: current_type=t; current=1
        if t=="V": max_w=max(max_w,current)
        else: max_l=max(max_l,current)
    return current_type,current,max_w,max_l

def h2h(a,b):
    return partidas[
        ((partidas["Jogador 1"]==a)&(partidas["Jogador 2"]==b)) |
        ((partidas["Jogador 1"]==b)&(partidas["Jogador 2"]==a))
    ].copy().sort_values(["Data","Horário","Ordem Entrada"],ascending=False)

def fmt_date(df):
    df=df.copy()
    df["Data"]=df["Data"].dt.strftime("%d/%m/%Y")
    return df

st.sidebar.markdown("## 🏓 TABLE TENNIS")
st.sidebar.markdown("### ANALYTICS")
page=st.sidebar.radio(
    "Navegação",
    [
      "Dashboard","Jogos do Dia","Jogadores","Confrontos (H2H)",
      "Análise Individual","Desempenho por Set","Sequências",
      "Rankings","Relatórios","Base de Dados"
    ],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")
st.sidebar.markdown("#### Resumo rápido")
st.sidebar.write(f"**Partidas:** {len(partidas)}")
st.sidebar.write(f"**Sets:** {len(sets)}")
st.sidebar.write(f"**Jogadores:** {len(nomes)}")
st.sidebar.write(f"**Média de pontos:** {partidas['Total Pontos'].mean():.1f}")
st.sidebar.caption("Match Intelligence v4.0")

if page=="Dashboard":
    hero("Dashboard","Visão geral do desempenho dos jogadores")

    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric("Total de partidas",len(partidas))
    c2.metric("Total de sets",len(sets))
    c3.metric("Total de jogadores",len(nomes))
    c4.metric("Média de pontos",f"{partidas['Total Pontos'].mean():.1f}")
    all_results=[]
    for n in nomes:
        pm=player_matches(n)
        ct,cn,mw,ml=streaks(pm["Resultado"].tolist())
        all_results.append((n,ct,cn,mw,ml))
    best_current=max(all_results,key=lambda x:x[2] if x[1]=="V" else 0)
    c5.metric("Melhor sequência atual",best_current[2],best_current[0])
    c6.metric("Jogos hoje",0)

    r1c1,r1c2,r1c3=st.columns([1.15,1.15,1])
    with r1c1:
        st.markdown('<div class="panel"><div class="panel-title">Sequências de vitórias</div>',unsafe_allow_html=True)
        seq=[]
        for n in nomes:
            pm=player_matches(n)
            ct,cn,mw,ml=streaks(pm["Resultado"].tolist())
            seq.append({"Jogador":n,"Sequência":cn if ct=="V" else 0})
        seq=pd.DataFrame(seq).sort_values("Sequência",ascending=False).head(5).set_index("Jogador")
        st.bar_chart(seq)
        st.markdown('</div>',unsafe_allow_html=True)
    with r1c2:
        st.markdown('<div class="panel"><div class="panel-title">Desempenho por set</div>',unsafe_allow_html=True)
        rows=[]
        for n in nomes[:5]:
            ps=player_sets(n)
            for sn in range(1,6):
                sub=ps[ps["Nº Set"]==sn]
                rows.append({"Jogador":n,"Set":sn,"Aproveitamento":sub["Venceu"].mean() if len(sub) else None})
        pivot=pd.DataFrame(rows).pivot(index="Jogador",columns="Set",values="Aproveitamento")
        st.dataframe(pivot.style.format("{:.0%}",na_rep="-"),use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with r1c3:
        st.markdown('<div class="panel"><div class="panel-title">Distribuição de resultados</div>',unsafe_allow_html=True)
        placares=(partidas["Sets J1"].astype(int).astype(str)+" × "+partidas["Sets J2"].astype(int).astype(str)).value_counts()
        st.dataframe(placares.rename_axis("Placar").reset_index(name="Quantidade"),use_container_width=True,hide_index=True)
        st.markdown('</div>',unsafe_allow_html=True)

    r2c1,r2c2,r2c3=st.columns([1.1,1,1.1])
    with r2c1:
        st.markdown('<div class="panel"><div class="panel-title">Top 5 — média de pontos</div>',unsafe_allow_html=True)
        rows=[]
        for n in nomes:
            pm=player_matches(n)
            rows.append({"Jogador":n,"Média":pm["Pontos Feitos"].mean()})
        top=pd.DataFrame(rows).sort_values("Média",ascending=False).head(5).set_index("Jogador")
        st.bar_chart(top)
        st.markdown('</div>',unsafe_allow_html=True)
    with r2c2:
        st.markdown('<div class="panel"><div class="panel-title">H2H rápido</div>',unsafe_allow_html=True)
        a=st.selectbox("Jogador A",nomes,index=0,key="dash_a")
        b=st.selectbox("Jogador B",[x for x in nomes if x!=a],index=0,key="dash_b")
        df=h2h(a,b)
        if df.empty:
            st.info("Sem confrontos")
        else:
            va=int((df["Vencedor"]==a).sum()); vb=int((df["Vencedor"]==b).sum())
            x1,x2,x3=st.columns(3)
            x1.metric(a,va,"vitórias")
            x2.metric("Jogos",len(df))
            x3.metric(b,vb,"vitórias")
        st.markdown('</div>',unsafe_allow_html=True)
    with r2c3:
        st.markdown('<div class="panel"><div class="panel-title">Queda de desempenho</div>',unsafe_allow_html=True)
        rows=[]
        for n in nomes[:5]:
            ps=player_sets(n)
            s1=ps[ps["Nº Set"]==1]["Venceu"].mean()
            last=ps[ps["Nº Set"]==ps["Nº Set"].max()]["Venceu"].mean()
            rows.append({"Jogador":n,"Variação":(last-s1) if pd.notna(s1) and pd.notna(last) else 0})
        st.bar_chart(pd.DataFrame(rows).set_index("Jogador"))
        st.markdown('</div>',unsafe_allow_html=True)

    st.markdown('<div class="panel-title" style="margin-top:18px">Últimos jogos</div>',unsafe_allow_html=True)
    ult=fmt_date(partidas.sort_values(["Data","Horário"],ascending=False).head(8))
    st.dataframe(ult[["Data","Horário","Jogador 1","Jogador 2","Sets J1","Sets J2","Vencedor","Total Pontos"]],
                 use_container_width=True,hide_index=True)

elif page=="Jogadores":
    hero("Jogadores","Resumo completo de todos os jogadores")
    rows=[]
    for n in nomes:
        pm=player_matches(n)
        vit=(pm["Resultado"]=="Vitória").sum()
        ct,cn,mw,ml=streaks(pm["Resultado"].tolist())
        rows.append({
            "Jogador":n,"Partidas":len(pm),"Vitórias":vit,"Derrotas":len(pm)-vit,
            "Aproveitamento":vit/len(pm) if len(pm) else 0,
            "Média pontos":pm["Pontos Feitos"].mean(),
            "Saldo médio":(pm["Pontos Feitos"]-pm["Pontos Sofridos"]).mean(),
            "Sequência atual":f"{cn} {'V' if ct=='V' else 'D'}"
        })
    st.dataframe(pd.DataFrame(rows).style.format({
        "Aproveitamento":"{:.1%}","Média pontos":"{:.1f}","Saldo médio":"{:.1f}"
    }),use_container_width=True,hide_index=True)

elif page=="Confrontos (H2H)":
    hero("Confrontos H2H","Pesquise dois jogadores e veja o histórico completo")
    c1,c2=st.columns(2)
    a=c1.selectbox("Jogador A",nomes,index=0)
    b=c2.selectbox("Jogador B",[x for x in nomes if x!=a],index=0)
    df=h2h(a,b)
    if df.empty:
        st.warning("Não existem confrontos registrados.")
    else:
        va=int((df["Vencedor"]==a).sum()); vb=int((df["Vencedor"]==b).sum())
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Confrontos",len(df))
        m2.metric(f"Vitórias {a}",va)
        m3.metric(f"Vitórias {b}",vb)
        m4.metric("Média de pontos",f"{df['Total Pontos'].mean():.1f}")
        tabs=st.tabs(["Histórico completo","Por set","Placares","Posição"])
        with tabs[0]:
            st.dataframe(fmt_date(df)[["Data","Horário","Jogador 1","Jogador 2","Sets J1","Sets J2","Vencedor","Total Pontos"]],
                         use_container_width=True,hide_index=True)
        with tabs[1]:
            hs=sets[
                ((sets["Jogador 1"]==a)&(sets["Jogador 2"]==b)) |
                ((sets["Jogador 1"]==b)&(sets["Jogador 2"]==a))
            ].copy()
            hs["Venceu A"]=hs["Vencedor Set"].eq(a)
            tab=hs.groupby("Nº Set").agg(Disputados=("ID Set","count"),Vitórias_A=("Venceu A","sum"),Média_total=("Total Set","mean")).reset_index()
            tab["Vitórias_B"]=tab["Disputados"]-tab["Vitórias_A"]
            tab["Aproveitamento_A"]=tab["Vitórias_A"]/tab["Disputados"]
            st.dataframe(tab.style.format({"Aproveitamento_A":"{:.1%}","Média_total":"{:.1f}"}),use_container_width=True,hide_index=True)
        with tabs[2]:
            plac=(df["Sets J1"].astype(int).astype(str)+" × "+df["Sets J2"].astype(int).astype(str)).value_counts()
            st.dataframe(plac.rename_axis("Placar").reset_index(name="Quantidade"),use_container_width=True,hide_index=True)
        with tabs[3]:
            rows=[]
            for n in [a,b]:
                for pos,col in [("J1","Jogador 1"),("J2","Jogador 2")]:
                    sub=df[df[col]==n]
                    rows.append({"Jogador":n,"Posição":pos,"Partidas":len(sub),"Vitórias":int((sub["Vencedor"]==n).sum())})
            pos=pd.DataFrame(rows)
            pos["Aproveitamento"]=pos.apply(lambda r:0 if r["Partidas"]==0 else r["Vitórias"]/r["Partidas"],axis=1)
            st.dataframe(pos.style.format({"Aproveitamento":"{:.1%}"}),use_container_width=True,hide_index=True)

elif page=="Análise Individual":
    hero("Análise Individual","Padrões completos de um jogador")
    n=st.selectbox("Pesquisar jogador",nomes)
    pm=player_matches(n); ps=player_sets(n)
    vit=int((pm["Resultado"]=="Vitória").sum()); ct,cn,mw,ml=streaks(pm["Resultado"].tolist())
    c1,c2,c3,c4,c5,c6=st.columns(6)
    c1.metric("Partidas",len(pm)); c2.metric("Vitórias",vit); c3.metric("Derrotas",len(pm)-vit)
    c4.metric("Aproveitamento",f"{vit/len(pm):.1%}"); c5.metric("Sequência atual",f"{cn} {'V' if ct=='V' else 'D'}")
    c6.metric("Saldo médio",f"{(pm['Pontos Feitos']-pm['Pontos Sofridos']).mean():.1f}")
    tabs=st.tabs(["Últimos jogos","Força por set","Placares","Adversários","Histórico completo"])
    with tabs[0]:
        st.dataframe(fmt_date(pm.sort_values(["Data","Horário"],ascending=False).head(10))[["Data","Horário","Adversário","Placar","Resultado","Pontos Feitos","Pontos Sofridos"]],
                     use_container_width=True,hide_index=True)
    with tabs[1]:
        bs=ps.groupby("Nº Set").agg(Sets=("ID Set","count"),Vitórias=("Venceu","sum"),Média_feitos=("Pontos Feitos","mean"),Média_sofridos=("Pontos Sofridos","mean")).reset_index()
        bs["Aproveitamento"]=bs["Vitórias"]/bs["Sets"]; bs["Saldo"]=bs["Média_feitos"]-bs["Média_sofridos"]
        st.dataframe(bs.style.format({"Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}","Média_sofridos":"{:.1f}","Saldo":"{:.1f}"}),
                     use_container_width=True,hide_index=True)
    with tabs[2]:
        vc=pm[pm["Resultado"]=="Vitória"]["Placar"].value_counts()
        dc=pm[pm["Resultado"]=="Derrota"]["Placar"].value_counts()
        c1,c2=st.columns(2)
        c1.dataframe(vc.rename_axis("Vitórias por placar").reset_index(name="Quantidade"),use_container_width=True,hide_index=True)
        c2.dataframe(dc.rename_axis("Derrotas por placar").reset_index(name="Quantidade"),use_container_width=True,hide_index=True)
    with tabs[3]:
        adv=pm.groupby("Adversário").agg(Partidas=("Resultado","size"),Vitórias=("Resultado",lambda x:(x=="Vitória").sum()),Média_feitos=("Pontos Feitos","mean"),Média_sofridos=("Pontos Sofridos","mean")).reset_index()
        adv["Aproveitamento"]=adv["Vitórias"]/adv["Partidas"]
        st.dataframe(adv.style.format({"Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}","Média_sofridos":"{:.1f}"}),use_container_width=True,hide_index=True)
    with tabs[4]:
        st.dataframe(fmt_date(pm.sort_values(["Data","Horário"],ascending=False)),use_container_width=True,hide_index=True)

elif page=="Desempenho por Set":
    hero("Desempenho por Set","Compare a força dos jogadores em cada set")
    n=st.selectbox("Jogador",nomes)
    ps=player_sets(n)
    bs=ps.groupby("Nº Set").agg(Sets=("ID Set","count"),Vitórias=("Venceu","sum"),Média_feitos=("Pontos Feitos","mean"),Média_sofridos=("Pontos Sofridos","mean")).reset_index()
    bs["Aproveitamento"]=bs["Vitórias"]/bs["Sets"]; bs["Saldo"]=bs["Média_feitos"]-bs["Média_sofridos"]
    st.dataframe(bs.style.format({"Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}","Média_sofridos":"{:.1f}","Saldo":"{:.1f}"}),use_container_width=True,hide_index=True)
    st.line_chart(bs.set_index("Nº Set")[["Aproveitamento"]])

elif page=="Sequências":
    hero("Sequências","Forma atual e maiores sequências")
    rows=[]
    for n in nomes:
        pm=player_matches(n)
        ct,cn,mw,ml=streaks(pm["Resultado"].tolist())
        rows.append({"Jogador":n,"Atual":f"{cn} {'vitórias' if ct=='V' else 'derrotas'}","Maior sequência de vitórias":mw,"Maior sequência de derrotas":ml})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

elif page=="Rankings":
    hero("Rankings","Classificação por aproveitamento e produção")
    rows=[]
    for n in nomes:
        pm=player_matches(n); vit=(pm["Resultado"]=="Vitória").sum()
        rows.append({"Jogador":n,"Partidas":len(pm),"Vitórias":vit,"Aproveitamento":vit/len(pm) if len(pm) else 0,"Média pontos":pm["Pontos Feitos"].mean(),"Saldo médio":(pm["Pontos Feitos"]-pm["Pontos Sofridos"]).mean()})
    rank=pd.DataFrame(rows).sort_values(["Aproveitamento","Vitórias"],ascending=False)
    st.dataframe(rank.style.format({"Aproveitamento":"{:.1%}","Média pontos":"{:.1f}","Saldo médio":"{:.1f}"}),use_container_width=True,hide_index=True)

elif page=="Jogos do Dia":
    hero("Jogos do Dia","Consulte partidas por data")
    dates=sorted(partidas["Data"].dropna().dt.date.unique(),reverse=True)
    d=st.selectbox("Data",dates)
    df=partidas[partidas["Data"].dt.date==d].sort_values(["Horário","Ordem Entrada"])
    st.dataframe(df[["Horário","Jogador 1","Jogador 2","Sets J1","Sets J2","Vencedor","Total Pontos","Qtd. Sets"]],
                 use_container_width=True,hide_index=True)

elif page=="Relatórios":
    hero("Relatórios","Resumo geral da base")
    st.write("Use as telas de análise para relatórios detalhados por jogador, duelo, set e sequência.")
    st.download_button("Baixar partidas.csv",(BASE/"partidas.csv").read_bytes(),file_name="partidas.csv")
    st.download_button("Baixar sets.csv",(BASE/"sets.csv").read_bytes(),file_name="sets.csv")

elif page=="Base de Dados":
    hero("Base de Dados","Todos os registros oficiais")
    t1,t2=st.tabs(["Partidas","Sets"])
    with t1: st.dataframe(partidas,use_container_width=True,hide_index=True)
    with t2: st.dataframe(sets,use_container_width=True,hide_index=True)
