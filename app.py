import re
import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Match Intelligence v5",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE = Path(__file__).parent

st.markdown("""
<style>
:root{
  --bg:#07101C; --panel:#0E192A; --panel2:#122238; --line:#24364D;
  --text:#F8FAFC; --muted:#94A3B8; --blue:#2F80ED; --green:#22C55E;
  --red:#EF4444; --amber:#F59E0B;
}
.stApp{background:linear-gradient(180deg,#07101C,#0A1422);}
.block-container{padding-top:1.1rem;max-width:1600px;}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#091524,#0D1B2E);
  border-right:1px solid #1B2B41;
}
[data-testid="stSidebar"] *{color:#F8FAFC;}
.hero{
  background:linear-gradient(135deg,#0D1B2E,#15365B);
  border:1px solid #284969;border-radius:18px;padding:22px 25px;
  box-shadow:0 16px 35px rgba(0,0,0,.25);margin-bottom:16px;
}
.hero h1{color:#FFF;margin:0;font-size:2rem;font-weight:850;}
.hero p{color:#A9BCD3;margin:.35rem 0 0;}
.answer{
  background:#0E192A;border:1px solid #2A405B;border-left:5px solid #2F80ED;
  border-radius:12px;padding:16px 18px;margin:10px 0;color:#E6EEF8;
}
.answer strong{color:#FFF;}
.insight{
  background:linear-gradient(180deg,#102239,#0E192A);
  border:1px solid #2A405B;border-radius:13px;padding:14px 16px;margin-bottom:10px;
}
.insight-title{color:#93C5FD;font-size:.78rem;font-weight:800;text-transform:uppercase;}
.insight-text{color:#F8FAFC;font-weight:700;margin-top:5px;}
.insight-sub{color:#94A3B8;font-size:.82rem;margin-top:5px;}
div[data-testid="stMetric"]{
  background:linear-gradient(180deg,#122137,#0F1B2D);
  border:1px solid #24364D;padding:15px 17px;border-radius:14px;
}
div[data-baseweb="select"]>div, div[data-baseweb="input"]>div{
  background:#0F1B2D!important;border:1px solid #31455E!important;
  border-radius:10px!important;color:white!important;
}
input{color:white!important;}
.stTabs [data-baseweb="tab"]{
  background:#0E192A;border:1px solid #263A53;color:#AFC1D8;border-radius:9px 9px 0 0;
}
.stTabs [aria-selected="true"]{background:#173454!important;color:#FFF!important;}
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
    return p, s, j

partidas, sets, jogadores = load_data()
nomes = sorted(set(partidas["Jogador 1"].dropna()) | set(partidas["Jogador 2"].dropna()))

DIAS = {
    0:"segunda-feira",1:"terça-feira",2:"quarta-feira",3:"quinta-feira",
    4:"sexta-feira",5:"sábado",6:"domingo"
}

def hero(title, subtitle):
    st.markdown(f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

def norm(txt):
    txt = unicodedata.normalize("NFD", str(txt))
    txt = "".join(c for c in txt if unicodedata.category(c) != "Mn")
    return txt.lower().strip()

def pct(a,b):
    return 0 if not b else a/b

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
    df["Placar"] = df["Sets Feitos"].astype(int).astype(str)+"×"+df["Sets Sofridos"].astype(int).astype(str)
    df["Dia da semana"] = df["Data"].dt.dayofweek.map(DIAS)
    df["Hora"] = pd.to_datetime(df["Horário"], format="%H:%M", errors="coerce").dt.hour
    return df.sort_values(["Data","Horário","Ordem Entrada"])

def player_sets(name):
    df=sets[(sets["Jogador 1"]==name)|(sets["Jogador 2"]==name)].copy()
    if df.empty:return df
    df["Pontos Feitos"]=df.apply(lambda r:r["Pontos J1"] if r["Jogador 1"]==name else r["Pontos J2"],axis=1)
    df["Pontos Sofridos"]=df.apply(lambda r:r["Pontos J2"] if r["Jogador 1"]==name else r["Pontos J1"],axis=1)
    df["Venceu"]=df["Vencedor Set"].eq(name)
    return df

def streaks(results):
    cur_t=None; cur=0; max_w=0; max_l=0
    for r in results:
        t="V" if r=="Vitória" else "D"
        if t==cur_t: cur+=1
        else: cur_t=t; cur=1
        if t=="V": max_w=max(max_w,cur)
        else: max_l=max(max_l,cur)
    return cur_t,cur,max_w,max_l

def h2h(a,b):
    return partidas[
        ((partidas["Jogador 1"]==a)&(partidas["Jogador 2"]==b)) |
        ((partidas["Jogador 1"]==b)&(partidas["Jogador 2"]==a))
    ].copy().sort_values(["Data","Horário","Ordem Entrada"],ascending=False)

def set_summary(name):
    ps=player_sets(name)
    if ps.empty:return pd.DataFrame()
    out=ps.groupby("Nº Set").agg(
        Disputados=("ID Set","count"),
        Vitórias=("Venceu","sum"),
        Média_feitos=("Pontos Feitos","mean"),
        Média_sofridos=("Pontos Sofridos","mean")
    ).reset_index()
    out["Derrotas"]=out["Disputados"]-out["Vitórias"]
    out["Aproveitamento"]=out["Vitórias"]/out["Disputados"]
    out["Saldo"]=out["Média_feitos"]-out["Média_sofridos"]
    return out

def first_set_stats(name):
    pm=player_matches(name)
    ps=player_sets(name)
    fs=ps[ps["Nº Set"]==1][["ID Partida","Venceu"]]
    m=pm.merge(fs,on="ID Partida",how="left")
    won=m[m["Venceu"]==True]
    lost=m[m["Venceu"]==False]
    return {
        "venceu_primeiro":len(won),
        "perdeu_primeiro":len(lost),
        "confirmou":int((won["Resultado"]=="Vitória").sum()),
        "virou":int((lost["Resultado"]=="Vitória").sum()),
    }

def auto_insights(name):
    pm=player_matches(name)
    ss=set_summary(name)
    fs=first_set_stats(name)
    vit=int((pm["Resultado"]=="Vitória").sum())
    ct,cn,mw,ml=streaks(pm["Resultado"].tolist())
    best=ss.sort_values(["Aproveitamento","Saldo"],ascending=False).iloc[0]
    worst=ss.sort_values(["Aproveitamento","Saldo"],ascending=True).iloc[0]
    day=pm.groupby("Dia da semana")["Resultado"].apply(lambda x:(x=="Vitória").mean()).sort_values(ascending=False)
    hour=pm.groupby("Hora")["Resultado"].apply(lambda x:(x=="Vitória").mean()).sort_values(ascending=False)
    return [
        ("FORMA ATUAL", f"{cn} {'vitórias' if ct=='V' else 'derrotas'} consecutivas.",
         f"Maior sequência positiva: {mw}. Maior sequência negativa: {ml}."),
        ("SET MAIS FORTE", f"{int(best['Nº Set'])}º set — {best['Aproveitamento']:.1%} de aproveitamento.",
         f"{int(best['Vitórias'])} vitórias em {int(best['Disputados'])} disputados."),
        ("SET MAIS FRACO", f"{int(worst['Nº Set'])}º set — {worst['Aproveitamento']:.1%} de aproveitamento.",
         f"{int(worst['Derrotas'])} derrotas em {int(worst['Disputados'])} disputados."),
        ("PRIMEIRO SET", f"Venceu {fs['venceu_primeiro']} e perdeu {fs['perdeu_primeiro']} primeiros sets.",
         f"Confirmação: {pct(fs['confirmou'],fs['venceu_primeiro']):.1%}. Viradas: {pct(fs['virou'],fs['perdeu_primeiro']):.1%}."),
        ("MELHOR DIA", f"{day.index[0]} — {day.iloc[0]:.1%} de aproveitamento.",
         "Calculado com os jogos registrados na base atual."),
        ("MELHOR HORÁRIO", f"{int(hour.index[0]):02d}h — {hour.iloc[0]:.1%} de aproveitamento.",
         "Calculado pelo horário inicial da partida."),
    ]

def find_players_in_question(q):
    nq=norm(q)
    found=[]
    for n in nomes:
        if norm(n) in nq or any(part in nq for part in norm(n).split() if len(part)>=5):
            found.append(n)
    # preserve uniqueness
    result=[]
    for n in found:
        if n not in result: result.append(n)
    return result

def answer_question(question):
    q=norm(question)
    found=find_players_in_question(question)

    if not question.strip():
        return "Digite uma pergunta sobre os dados registrados.", None

    if "maior sequencia" in q and ("vitoria" in q or "ganh" in q):
        rows=[]
        for n in nomes:
            pm=player_matches(n)
            _,_,mw,_=streaks(pm["Resultado"].tolist())
            rows.append((n,mw))
        n,v=max(rows,key=lambda x:x[1])
        return f"{n} possui a maior sequência de vitórias da base: {v} partidas consecutivas.", None

    if "mais vitorias por 3x0" in q or "mais venceu por 3x0" in q:
        rows=[]
        for n in nomes:
            pm=player_matches(n)
            rows.append((n,int(((pm["Resultado"]=="Vitória")&(pm["Placar"]=="3×0")).sum())))
        n,v=max(rows,key=lambda x:x[1])
        return f"{n} é quem mais venceu por 3×0: {v} vez(es).", None

    if "mais forte" in q and "set" in q and not found:
        m=re.search(r"([1-5])",q)
        if m:
            sn=int(m.group(1))
            rows=[]
            for n in nomes:
                ss=set_summary(n)
                sub=ss[ss["Nº Set"]==sn]
                if not sub.empty: rows.append((n,float(sub.iloc[0]["Aproveitamento"]),int(sub.iloc[0]["Disputados"])))
            n,a,d=max(rows,key=lambda x:x[1])
            return f"{n} tem o melhor aproveitamento no {sn}º set: {a:.1%}, em {d} sets disputados.", None

    if len(found)>=2:
        a,b=found[:2]
        df=h2h(a,b)
        if df.empty:
            return f"Não existem confrontos registrados entre {a} e {b}.", None
        va=int((df["Vencedor"]==a).sum())
        vb=int((df["Vencedor"]==b).sum())
        if "quantos" in q or "jogos" in q or "confront" in q:
            return f"{a} e {b} possuem {len(df)} confronto(s): {va} vitória(s) de {a} e {vb} de {b}.", df
        if "ultimo" in q or "recent" in q:
            r=df.iloc[0]
            return f"O confronto mais recente foi vencido por {r['Vencedor']}, por {int(r['Sets J1'])}×{int(r['Sets J2'])}, em {r['Data'].strftime('%d/%m/%Y')}.", df.head(5)
        return f"No H2H, {a} tem {va} vitória(s) e {b} tem {vb}, em {len(df)} jogos.", df

    if found:
        n=found[0]
        pm=player_matches(n)
        ss=set_summary(n)
        fs=first_set_stats(n)

        if "quantos jogos" in q or "quantas partidas" in q:
            return f"{n} possui {len(pm)} partidas registradas.", pm

        if "historico" in q or "todos os jogos" in q:
            return f"A base contém {len(pm)} jogos de {n}. A tabela abaixo mostra o histórico completo.", pm.sort_values(["Data","Horário"],ascending=False)

        if "dia da semana" in q or "qual dia" in q:
            tab=pm.groupby("Dia da semana").agg(
                Jogos=("Resultado","size"),
                Vitórias=("Resultado",lambda x:(x=="Vitória").sum())
            ).reset_index()
            tab["Aproveitamento"]=tab["Vitórias"]/tab["Jogos"]
            best=tab.sort_values(["Aproveitamento","Jogos"],ascending=False).iloc[0]
            return f"{n} tem melhor aproveitamento na {best['Dia da semana']}: {best['Aproveitamento']:.1%}, em {int(best['Jogos'])} jogo(s).", tab

        if "horario" in q or "hora" in q:
            tab=pm.groupby("Hora").agg(
                Jogos=("Resultado","size"),
                Vitórias=("Resultado",lambda x:(x=="Vitória").sum())
            ).reset_index()
            tab["Aproveitamento"]=tab["Vitórias"]/tab["Jogos"]
            best=tab.sort_values(["Aproveitamento","Jogos"],ascending=False).iloc[0]
            return f"O melhor horário registrado de {n} é {int(best['Hora']):02d}h, com {best['Aproveitamento']:.1%} de aproveitamento.", tab

        m=re.search(r"([1-5])",q)
        if m and "set" in q:
            sn=int(m.group(1))
            row=ss[ss["Nº Set"]==sn]
            if row.empty:
                return f"{n} não possui {sn}º set registrado.", None
            r=row.iloc[0]
            if "perdeu" in q or "derrota" in q:
                return f"{n} perdeu o {sn}º set {int(r['Derrotas'])} vez(es), em {int(r['Disputados'])} disputados.", row
            return f"{n} venceu o {sn}º set {int(r['Vitórias'])} vez(es), em {int(r['Disputados'])} disputados. Aproveitamento: {r['Aproveitamento']:.1%}.", row

        if "3x0" in q or "0x3" in q or "3 a 0" in q:
            w=int(((pm["Resultado"]=="Vitória")&(pm["Placar"]=="3×0")).sum())
            l=int(((pm["Resultado"]=="Derrota")&(pm["Placar"]=="0×3")).sum())
            if "perdeu" in q:
                return f"{n} perdeu por 0×3 {l} vez(es).", pm[pm["Placar"]=="0×3"]
            return f"{n} venceu por 3×0 {w} vez(es) e perdeu por 0×3 {l} vez(es).", pm[pm["Placar"].isin(["3×0","0×3"])]

        if "3x1" in q or "1x3" in q or "quatro sets" in q:
            w=int(((pm["Resultado"]=="Vitória")&(pm["Placar"]=="3×1")).sum())
            l=int(((pm["Resultado"]=="Derrota")&(pm["Placar"]=="1×3")).sum())
            return f"{n} venceu por 3×1 {w} vez(es) e perdeu por 1×3 {l} vez(es).", pm[pm["Placar"].isin(["3×1","1×3"])]

        if "primeiro set" in q:
            if "perdeu" in q:
                return f"{n} perdeu o primeiro set {fs['perdeu_primeiro']} vez(es).", None
            return f"{n} venceu o primeiro set {fs['venceu_primeiro']} vez(es).", None

        if "melhor set" in q or "mais forte" in q:
            r=ss.sort_values(["Aproveitamento","Saldo"],ascending=False).iloc[0]
            return f"O set mais forte de {n} é o {int(r['Nº Set'])}º, com {r['Aproveitamento']:.1%} de aproveitamento.", ss

        if "pior set" in q or "mais fraco" in q or "queda" in q:
            r=ss.sort_values(["Aproveitamento","Saldo"],ascending=True).iloc[0]
            return f"O set mais fraco de {n} é o {int(r['Nº Set'])}º, com {r['Aproveitamento']:.1%} de aproveitamento.", ss

        return f"{n} possui {len(pm)} jogos, com {(pm['Resultado']=='Vitória').sum()} vitórias e {(pm['Resultado']=='Derrota').sum()} derrotas.", pm

    return (
        "Não consegui identificar exatamente a pergunta. Tente mencionar o nome do jogador e o assunto, "
        "por exemplo: “Quantas vezes Dronova perdeu o primeiro set?”",
        None
    )

st.sidebar.markdown("## 🏓 MATCH INTELLIGENCE")
st.sidebar.caption("Central de respostas analíticas")
page=st.sidebar.radio(
    "",
    ["Central de Respostas","Análise Automática","Comparador H2H","Histórico","Base de Dados"],
    label_visibility="collapsed"
)
st.sidebar.markdown("---")
st.sidebar.write(f"**Partidas:** {len(partidas)}")
st.sidebar.write(f"**Sets:** {len(sets)}")
st.sidebar.write(f"**Jogadores:** {len(nomes)}")
st.sidebar.caption("Base oficial atual")

if page=="Central de Respostas":
    hero("Pergunte ao banco","Faça perguntas em linguagem natural sobre jogadores, sets, placares, horários e confrontos.")

    exemplos=[
        "Quantas vezes Dronova Ulana perdeu o primeiro set?",
        "Qual é o pior set de Yana Mykhailyk?",
        "Quantos jogos existem entre Dronova Ulana e Plashchynska Anhelina?",
        "Quem possui a maior sequência de vitórias?",
        "Quem venceu mais partidas por 3x0?",
    ]
    pergunta=st.text_input("Digite sua pergunta",placeholder="Ex.: Quantas vezes Yana perdeu o terceiro set?")
    with st.expander("Exemplos de perguntas"):
        for e in exemplos: st.write("•",e)

    if pergunta:
        resposta,evidencia=answer_question(pergunta)
        st.markdown(f'<div class="answer"><strong>Resposta:</strong><br>{resposta}</div>',unsafe_allow_html=True)
        if evidencia is not None and len(evidencia):
            st.markdown("### Evidências usadas")
            ev=evidencia.copy()
            if "Data" in ev.columns and pd.api.types.is_datetime64_any_dtype(ev["Data"]):
                ev["Data"]=ev["Data"].dt.strftime("%d/%m/%Y")
            st.dataframe(ev,use_container_width=True,hide_index=True)

elif page=="Análise Automática":
    hero("Análise Automática","Selecione um jogador e veja as respostas mais importantes sem precisar interpretar tabelas.")
    n=st.selectbox("Jogador",nomes)
    pm=player_matches(n)
    ss=set_summary(n)
    vit=int((pm["Resultado"]=="Vitória").sum())
    ct,cn,mw,ml=streaks(pm["Resultado"].tolist())

    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Jogos",len(pm))
    c2.metric("Vitórias",vit)
    c3.metric("Derrotas",len(pm)-vit)
    c4.metric("Aproveitamento",f"{pct(vit,len(pm)):.1%}")
    c5.metric("Sequência atual",f"{cn} {'V' if ct=='V' else 'D'}")

    st.markdown("### Respostas automáticas")
    cols=st.columns(3)
    for i,(title,text,sub) in enumerate(auto_insights(n)):
        with cols[i%3]:
            st.markdown(
                f'<div class="insight"><div class="insight-title">{title}</div>'
                f'<div class="insight-text">{text}</div><div class="insight-sub">{sub}</div></div>',
                unsafe_allow_html=True
            )

    tabs=st.tabs(["Todos os jogos","Sets","Placares","Dias e horários"])
    with tabs[0]:
        x=pm.sort_values(["Data","Horário"],ascending=False).copy()
        x["Data"]=x["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(x[["Data","Horário","Adversário","Posição","Placar","Resultado","Pontos Feitos","Pontos Sofridos"]],
                     use_container_width=True,hide_index=True)
    with tabs[1]:
        st.dataframe(ss.style.format({
            "Aproveitamento":"{:.1%}","Média_feitos":"{:.1f}",
            "Média_sofridos":"{:.1f}","Saldo":"{:.1f}"
        }),use_container_width=True,hide_index=True)
    with tabs[2]:
        plac=pm.groupby(["Resultado","Placar"]).size().reset_index(name="Quantidade")
        st.dataframe(plac,use_container_width=True,hide_index=True)
    with tabs[3]:
        by_day=pm.groupby("Dia da semana").agg(Jogos=("Resultado","size"),Vitórias=("Resultado",lambda x:(x=="Vitória").sum())).reset_index()
        by_day["Aproveitamento"]=by_day["Vitórias"]/by_day["Jogos"]
        by_hour=pm.groupby("Hora").agg(Jogos=("Resultado","size"),Vitórias=("Resultado",lambda x:(x=="Vitória").sum())).reset_index()
        by_hour["Aproveitamento"]=by_hour["Vitórias"]/by_hour["Jogos"]
        c1,c2=st.columns(2)
        c1.dataframe(by_day.style.format({"Aproveitamento":"{:.1%}"}),use_container_width=True,hide_index=True)
        c2.dataframe(by_hour.style.format({"Aproveitamento":"{:.1%}"}),use_container_width=True,hide_index=True)

elif page=="Comparador H2H":
    hero("Comparador H2H","Compare dois jogadores e receba uma leitura direta do confronto.")
    c1,c2=st.columns(2)
    a=c1.selectbox("Jogador A",nomes,index=0)
    b=c2.selectbox("Jogador B",[x for x in nomes if x!=a],index=0)
    df=h2h(a,b)
    if df.empty:
        st.warning("Não existem confrontos registrados.")
    else:
        va=int((df["Vencedor"]==a).sum()); vb=int((df["Vencedor"]==b).sum())
        st.markdown(
            f'<div class="answer"><strong>Leitura do confronto:</strong><br>'
            f'{a} e {b} jogaram {len(df)} vez(es). {a} venceu {va}; {b} venceu {vb}. '
            f'O aproveitamento de {a} é {pct(va,len(df)):.1%}.</div>',
            unsafe_allow_html=True
        )
        x=df.copy(); x["Data"]=x["Data"].dt.strftime("%d/%m/%Y")
        st.dataframe(x[["Data","Horário","Jogador 1","Jogador 2","Sets J1","Sets J2","Vencedor","Total Pontos"]],
                     use_container_width=True,hide_index=True)

elif page=="Histórico":
    hero("Histórico","Consulte todos os jogos de um jogador ou toda a base.")
    n=st.selectbox("Jogador",["Todos"]+nomes)
    df=partidas.copy() if n=="Todos" else player_matches(n)
    df=df.sort_values(["Data","Horário"],ascending=False).copy()
    df["Data"]=df["Data"].dt.strftime("%d/%m/%Y")
    st.dataframe(df,use_container_width=True,hide_index=True)

elif page=="Base de Dados":
    hero("Base de Dados","Registros oficiais usados nas respostas.")
    t1,t2=st.tabs(["Partidas","Sets"])
    with t1: st.dataframe(partidas,use_container_width=True,hide_index=True)
    with t2: st.dataframe(sets,use_container_width=True,hide_index=True)
