from pathlib import Path
import html
import pandas as pd
import streamlit as st

st.set_page_config(page_title='Match Intelligence', page_icon='🏓', layout='wide', initial_sidebar_state='expanded')
BASE = Path(__file__).parent

st.markdown('''
<style>
:root{--bg:#050B14;--panel:#0B1625;--line:#1D3047;--text:#F8FAFC;--muted:#91A4BC;--purple:#6D4AFF;--green:#22C55E;--red:#EF4444;--orange:#F59E0B}
.stApp{background:linear-gradient(180deg,#030812 0%,#08111E 100%)}
.block-container{max-width:1680px;padding:1rem 1.15rem 2rem 1.15rem!important;overflow:visible!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#050D18,#071321);border-right:1px solid #17283D;min-width:230px!important;max-width:230px!important}
[data-testid="stSidebar"] *{color:#F4F8FF!important;opacity:1!important;text-shadow:none!important}[data-testid="stSidebar"] .stRadio label{padding:.48rem .55rem!important;border-radius:8px!important;white-space:normal!important;line-height:1.2!important}
h1,h2,h3,h4,p,label,span{color:var(--text)}
div[data-testid="stMetric"]{background:linear-gradient(180deg,#0E1D30,#0A1524);border:1px solid #1D334D;padding:14px 16px;border-radius:13px;min-height:104px;box-shadow:0 12px 30px rgba(0,0,0,.24)}
div[data-testid="stMetricLabel"]{color:#B5C3D5;font-size:.77rem;text-transform:uppercase}
div[data-testid="stMetricValue"]{color:#FFF;font-weight:850}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div{background:#0B1625!important;border:1px solid #36516F!important;border-radius:10px!important;color:#FFFFFF!important;opacity:1!important;box-shadow:none!important}div[data-baseweb="select"] *{color:#FFFFFF!important;opacity:1!important}div[data-baseweb="select"] svg{fill:#FFFFFF!important;color:#FFFFFF!important;opacity:1!important}input{color:#FFFFFF!important;opacity:1!important}[data-baseweb="popover"]{background:#0B1625!important}[role="listbox"]{background:#0B1625!important;color:#FFFFFF!important}[role="option"]{background:#0B1625!important;color:#FFFFFF!important;opacity:1!important}[role="option"]:hover{background:#17304E!important}
.hero-kicker{color:#B7C4D4;font-size:.85rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}.hero-title{font-size:2rem;line-height:1.05;font-weight:900;color:#FFF}.hero-sub{color:#91A4BC;margin-top:.35rem}
.panel{background:linear-gradient(180deg,#0D1929,#091421);border:1px solid #1D334D;border-radius:14px;padding:15px;box-shadow:0 12px 28px rgba(0,0,0,.20);height:100%}.panel-title{font-weight:850;color:#F8FAFC;font-size:.94rem;text-transform:uppercase;margin-bottom:12px}.panel-sub{color:#8296AE;font-size:.78rem;margin-top:-7px;margin-bottom:10px}
.history-wrap{background:linear-gradient(180deg,#0C1828,#09131F);border:1px solid #1D334D;border-radius:14px;overflow-x:auto!important;overflow-y:hidden!important;width:100%!important}.history-head{display:grid;grid-template-columns:96px 62px minmax(130px,1fr) 56px minmax(145px,1.15fr) 56px 14px;gap:6px;padding:11px 12px;color:#B7C6D8;font-size:.68rem;font-weight:900;text-transform:uppercase;border-bottom:1px solid #1D3047;min-width:735px}.match-row{display:grid;grid-template-columns:96px 62px minmax(130px,1fr) 56px minmax(145px,1.15fr) 56px 14px;gap:6px;align-items:center;padding:10px 12px;border-bottom:1px solid #182A3E;min-width:735px}.match-row:hover{background:#101F32}.match-date,.match-time{color:#F4F8FF;font-size:.78rem;font-weight:650;white-space:nowrap}.opponent{color:#FFF;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.80rem;min-width:0}.avatar{display:inline-flex;width:23px;height:23px;border-radius:50%;align-items:center;justify-content:center;margin-right:6px;background:#1E62A9;color:#FFF!important;font-size:.62rem;font-weight:900;opacity:1!important;flex:0 0 auto}.sets-detail{color:#AFC0D4;font-size:.68rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.score{color:#FFF;font-weight:900;font-size:.88rem;text-align:center;white-space:nowrap}.result-badge{width:29px;height:29px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#FFF!important;font-weight:900;margin:auto;opacity:1!important;box-shadow:0 0 0 2px rgba(255,255,255,.06)}.result-win{background:linear-gradient(180deg,#22A447,#14843A)}.result-loss{background:linear-gradient(180deg,#EF3F3F,#BE2020)}.arrow{color:#6D86A3;font-size:1.2rem;text-align:right}
.form-strip{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 4px}.form-dot{width:25px;height:25px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:900;color:white}.form-win{background:#178C45}.form-loss{background:#CF2D2D}.spark{width:100%;height:70px;margin-top:6px}.spark-grid{stroke:#162A40;stroke-width:1}.spark-line{fill:none;stroke:#6CCB5F;stroke-width:2.4}
.set-row{display:grid;grid-template-columns:58px minmax(28px,1fr) 34px 34px 48px 72px;align-items:center;gap:5px;padding:8px 0;border-bottom:1px solid #182B40;min-width:0}.set-row:last-child{border-bottom:none}.set-name{font-weight:800;color:#FFF}.set-num,.set-pct,.set-avg{color:#F4F8FF;font-size:.72rem;text-align:center;white-space:nowrap;opacity:1!important}.progress{height:5px;border-radius:99px;background:#17273A;overflow:hidden;margin-top:5px}.progress>span{display:block;height:100%;border-radius:99px}
.score-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:10px}.score-column{background:#0A1522;border:1px solid #1B3048;border-radius:10px;padding:12px}.score-title{font-size:.74rem;font-weight:900;text-transform:uppercase;margin-bottom:8px}.score-line{display:grid;grid-template-columns:42px 1fr 38px;gap:8px;align-items:center;margin:9px 0}.score-label{font-weight:850;color:#FFF}.score-count{color:#B7C6D8;text-align:right;font-size:.82rem}.mini-bar{height:5px;border-radius:99px;background:#182A3E;overflow:hidden}.mini-bar span{display:block;height:100%;border-radius:99px}
.first-card{border-radius:12px;padding:15px;border:1px solid #24405D;background:#0A1624}.first-card.good{background:linear-gradient(180deg,#10271D,#0B1B16);border-color:#214C35}.first-card.bad{background:linear-gradient(180deg,#2B1619,#1B1014);border-color:#4B2329}.first-icon{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:1.15rem;font-weight:900;float:left;margin-right:12px}.first-value{font-size:1.18rem;font-weight:900;color:#FFF;white-space:nowrap}.first-label{font-size:.78rem;font-weight:850;color:#EAF1FB;text-transform:uppercase}.first-sub{font-size:.78rem;color:#91A4BC;margin-top:3px}
.analysis-box{border-radius:12px;border:1px solid #6D4AFF;background:linear-gradient(135deg,rgba(50,29,103,.34),rgba(10,20,35,.96));padding:16px}.analysis-title{font-weight:900;color:#FFF;margin-bottom:7px}.analysis-text{color:#C7D3E2;line-height:1.5}
.stTabs [data-baseweb="tab"]{background:#0B1625;border:1px solid #1D334D;color:#A6B8CD;border-radius:8px 8px 0 0}.stTabs [aria-selected="true"]{background:#21165A!important;color:#FFF!important;border-color:#6D4AFF!important}

[data-testid="stDataFrame"]{background:#0B1625!important;border:1px solid #1D334D!important;border-radius:12px!important;overflow:auto!important}
[data-testid="stDataFrame"] *{opacity:1!important}
[data-testid="stSelectbox"] label,[data-testid="stTextInput"] label{color:#F4F8FF!important;font-weight:750!important;opacity:1!important}
.stTabs [data-baseweb="tab-list"]{overflow-x:auto!important;gap:4px!important}
.stTabs [data-baseweb="tab"]{white-space:nowrap!important;min-width:max-content!important;padding:.55rem .72rem!important}
@media (max-width:1350px){
  .block-container{padding-left:.75rem!important;padding-right:.75rem!important}
  [data-testid="stSidebar"]{min-width:220px!important;max-width:220px!important}
  div[data-testid="stMetric"]{min-height:105px!important;padding:12px!important}
  div[data-testid="stMetricLabel"]{font-size:.66rem!important;line-height:1.15!important}
  div[data-testid="stMetricValue"]{font-size:1.55rem!important}
  .panel{padding:12px!important}
  .panel-title{font-size:.82rem!important}
}
@media (max-width:1050px){
  .history-head,.match-row{grid-template-columns:88px 54px minmax(110px,1fr) 52px 48px 10px;min-width:430px}
  .match-date,.match-time,.opponent{font-size:.72rem!important}
  .avatar{display:none!important}
  .score-grid{grid-template-columns:1fr!important}
  .first-value{font-size:1rem!important}
}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    p=pd.read_csv(BASE/'partidas.csv'); s=pd.read_csv(BASE/'sets.csv'); j=pd.read_csv(BASE/'jogadores.csv')
    p['Data']=pd.to_datetime(p['Data'],dayfirst=True,errors='coerce'); s['Data']=pd.to_datetime(s['Data'],dayfirst=True,errors='coerce')
    for c in ['Sets J1','Sets J2','Qtd. Sets','Total Pontos','Pontos J1','Pontos J2','Margem J1','Ordem Entrada']: p[c]=pd.to_numeric(p[c],errors='coerce')
    for c in ['Nº Set','Pontos J1','Pontos J2','Diferença J1','Total Set']: s[c]=pd.to_numeric(s[c],errors='coerce')
    return p,s,j

partidas,sets,jogadores=load_data()
nomes=sorted(set(partidas['Jogador 1'].dropna())|set(partidas['Jogador 2'].dropna()))

def pct(a,b): return 0 if b==0 else a/b

def player_matches(name):
    df=partidas[(partidas['Jogador 1']==name)|(partidas['Jogador 2']==name)].copy()
    if df.empty:return df
    df['Adversário']=df.apply(lambda r:r['Jogador 2'] if r['Jogador 1']==name else r['Jogador 1'],axis=1)
    df['Posição']=df['Jogador 1'].apply(lambda x:'J1' if x==name else 'J2')
    df['Sets Feitos']=df.apply(lambda r:r['Sets J1'] if r['Jogador 1']==name else r['Sets J2'],axis=1)
    df['Sets Sofridos']=df.apply(lambda r:r['Sets J2'] if r['Jogador 1']==name else r['Sets J1'],axis=1)
    df['Pontos Feitos']=df.apply(lambda r:r['Pontos J1'] if r['Jogador 1']==name else r['Pontos J2'],axis=1)
    df['Pontos Sofridos']=df.apply(lambda r:r['Pontos J2'] if r['Jogador 1']==name else r['Pontos J1'],axis=1)
    df['Resultado']=df['Vencedor'].eq(name).map({True:'Vitória',False:'Derrota'})
    df['Placar']=df['Sets Feitos'].astype(int).astype(str)+' - '+df['Sets Sofridos'].astype(int).astype(str)
    return df.sort_values(['Data','Horário','Ordem Entrada'])

def player_sets(name):
    df=sets[(sets['Jogador 1']==name)|(sets['Jogador 2']==name)].copy()
    if df.empty:return df
    df['Pontos Feitos']=df.apply(lambda r:r['Pontos J1'] if r['Jogador 1']==name else r['Pontos J2'],axis=1)
    df['Pontos Sofridos']=df.apply(lambda r:r['Pontos J2'] if r['Jogador 1']==name else r['Pontos J1'],axis=1)
    df['Venceu']=df['Vencedor Set'].eq(name)
    return df

def streak_data(results):
    current_type=None;current=0;max_w=0;max_l=0
    for r in results:
        t='V' if r=='Vitória' else 'D'
        if t==current_type:current+=1
        else:current_type=t;current=1
        if t=='V':max_w=max(max_w,current)
        else:max_l=max(max_l,current)
    return current_type,current,max_w,max_l

def set_summary(name):
    ps=player_sets(name)
    if ps.empty:return pd.DataFrame()
    result=ps.groupby('Nº Set').agg(Disputados=('ID Set','count'),Vitórias=('Venceu','sum'),Média_feitos=('Pontos Feitos','mean'),Média_sofridos=('Pontos Sofridos','mean')).reset_index()
    result['Derrotas']=result['Disputados']-result['Vitórias'];result['Aproveitamento']=result['Vitórias']/result['Disputados']
    return result

def first_set_stats(name):
    pm=player_matches(name); ps=player_sets(name); fs=ps[ps['Nº Set']==1][['ID Partida','Venceu']]; merged=pm.merge(fs,on='ID Partida',how='left')
    won=merged[merged['Venceu']==True]; lost=merged[merged['Venceu']==False]
    return {'won_first':len(won),'lost_first':len(lost),'confirmed':int((won['Resultado']=='Vitória').sum()),'comebacks':int((lost['Resultado']=='Vitória').sum())}

def initials(name): return ''.join([p[0] for p in str(name).split()[:2]]).upper()[:2]

def sets_detail(match_id,name):
    sm=sets[sets['ID Partida']==match_id].sort_values('Nº Set')
    vals=[]
    for _,r in sm.iterrows():
        a=int(r['Pontos J1']) if r['Jogador 1']==name else int(r['Pontos J2'])
        b=int(r['Pontos J2']) if r['Jogador 1']==name else int(r['Pontos J1'])
        vals.append(f'{a}-{b}')
    return ', '.join(vals)

def history_html(df,name):
    if df.empty:return '<div class="panel">Nenhuma partida encontrada.</div>'
    rows=[]
    for _,r in df.iterrows():
        cls='result-win' if r['Resultado']=='Vitória' else 'result-loss';letter='V' if r['Resultado']=='Vitória' else 'D';date=r['Data'].strftime('%d/%m/%Y') if pd.notna(r['Data']) else '-'
        rows.append(f'''<div class="match-row"><div class="match-date">{date}</div><div class="match-time">{html.escape(str(r['Horário']))}</div><div class="opponent"><span class="avatar">{html.escape(initials(r['Adversário']))}</span>{html.escape(str(r['Adversário']))}</div><div class="score">{html.escape(str(r['Placar']))}</div><div><div class="result-badge {cls}">{letter}</div></div><div class="arrow">›</div></div>''')
    return '<div class="history-wrap"><div class="history-head"><div>Data</div><div>Hora</div><div>Adversário</div><div>Placar</div><div>Sets</div><div>Resultado</div><div></div></div>'+''.join(rows)+'</div>'

def form_html(df,limit=10):
    recent=df.sort_values(['Data','Horário','Ordem Entrada'],ascending=False).head(limit);dots=[]
    for _,r in recent.iloc[::-1].iterrows():
        cls='form-win' if r['Resultado']=='Vitória' else 'form-loss';letter='V' if r['Resultado']=='Vitória' else 'D';dots.append(f'<span class="form-dot {cls}">{letter}</span>')
    return '<div class="form-strip">'+''.join(dots)+'</div>'

def spark_html(pm):
    recent=pm.sort_values(['Data','Horário','Ordem Entrada'],ascending=False).head(10).iloc[::-1]
    ys=[18 if r=='Vitória' else 52 for r in recent['Resultado']]
    xs=[8+i*(184/max(1,len(ys)-1)) for i in range(len(ys))]
    pts=' '.join(f'{x:.1f},{y}' for x,y in zip(xs,ys))
    circles=''.join(f'<circle cx="{x:.1f}" cy="{y}" r="3" fill="{"#22C55E" if y==18 else "#EF4444"}"/>' for x,y in zip(xs,ys))
    return f'<svg class="spark" viewBox="0 0 200 70"><line class="spark-grid" x1="5" y1="35" x2="195" y2="35"/><polyline class="spark-line" points="{pts}"/>{circles}</svg>'

def sets_html(summary):
    rows=[]
    for _,r in summary.iterrows():
        p=float(r['Aproveitamento']);color='#22C55E' if p>=.55 else '#F59E0B' if p>=.45 else '#EF4444';avg=f"{r['Média_feitos']:.1f} - {r['Média_sofridos']:.1f}"
        rows.append(f'''<div class="set-row"><div><div class="set-name">{int(r['Nº Set'])}º SET</div><div class="progress"><span style="width:{p*100:.1f}%;background:{color}"></span></div></div><div></div><div class="set-num">{int(r['Vitórias'])}</div><div class="set-num">{int(r['Derrotas'])}</div><div class="set-pct">{p:.1%}</div><div class="set-avg">{avg}</div></div>''')
    return '<div class="panel"><div class="panel-title">Desempenho por set</div><div class="set-row" style="padding-top:0"><div style="color:#91A4BC;font-size:.68rem">SET</div><div></div><div style="color:#91A4BC;font-size:.68rem;text-align:center">VIT.</div><div style="color:#91A4BC;font-size:.68rem;text-align:center">DER.</div><div style="color:#91A4BC;font-size:.68rem;text-align:center">APROV.</div><div style="color:#91A4BC;font-size:.68rem;text-align:center">MÉDIA</div></div>'+''.join(rows)+'</div>'

def scorelines_html(pm):
    wins=pm[pm['Resultado']=='Vitória']['Placar'].value_counts();losses=pm[pm['Resultado']=='Derrota']['Placar'].value_counts();max_count=max([1]+list(wins.values)+list(losses.values))
    def col(title,color,items):
        lines=[]
        for score,count in items:
            width=count/max_count*100;lines.append(f'<div class="score-line"><div class="score-label">{score}</div><div class="mini-bar"><span style="width:{width:.1f}%;background:{color}"></span></div><div class="score-count">{count}</div></div>')
        return f'<div class="score-column"><div class="score-title" style="color:{color}">{title}</div>'+''.join(lines)+'</div>'
    return '<div class="panel"><div class="panel-title">Placares mais frequentes</div><div class="score-grid">'+col('Vitórias','#22C55E',[(x,int(wins.get(x,0))) for x in ['3 - 0','3 - 1','3 - 2']])+col('Derrotas','#EF4444',[(x,int(losses.get(x,0))) for x in ['0 - 3','1 - 3','2 - 3']])+'</div></div>'

def first_set_html(stats):
    cr=pct(stats['confirmed'],stats['won_first']);vr=pct(stats['comebacks'],stats['lost_first'])
    return f'''<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div class="first-card good"><div class="first-icon" style="background:#159447">✓</div><div class="first-label">Após vencer o 1º set</div><div class="first-value">{stats['confirmed']} / {stats['won_first']} &nbsp; <span style="color:#4ADE80;font-size:1rem">{cr:.1%}</span></div><div class="first-sub">Venceu a partida</div><div style="clear:both"></div></div><div class="first-card bad"><div class="first-icon" style="background:#D92C2C">×</div><div class="first-label">Após perder o 1º set</div><div class="first-value">{stats['comebacks']} / {stats['lost_first']} &nbsp; <span style="color:#FB7185;font-size:1rem">{vr:.1%}</span></div><div class="first-sub">Virou a partida</div><div style="clear:both"></div></div></div>'''

st.sidebar.markdown('## 🏓 MATCH');st.sidebar.markdown('### INTELLIGENCE');st.sidebar.caption('ANÁLISE DE TÊNIS DE MESA')
page=st.sidebar.radio('Menu',['Dashboard','Jogos do Dia','Jogadores','Confrontos (H2H)','Pergunte ao Banco','Análise Individual','Desempenho por Set','Sequências','Horários','Dias da Semana','Placares','Viradas','Rankings','Relatórios','Configurações','Base de Dados'],label_visibility='collapsed')
st.sidebar.markdown('---');st.sidebar.markdown('#### BASE DE DADOS');st.sidebar.write(f'Partidas: **{len(partidas)}**');st.sidebar.write(f'Sets: **{len(sets)}**');st.sidebar.write(f'Jogadores: **{len(nomes)}**');st.sidebar.caption('● Base oficial ativa')

if page in ['Dashboard','Jogadores','Análise Individual']:
    selected=st.selectbox('Selecionar jogador',nomes,index=0);pm=player_matches(selected);ps=player_sets(selected);ss=set_summary(selected);fs=first_set_stats(selected)
    wins=int((pm['Resultado']=='Vitória').sum());losses=int((pm['Resultado']=='Derrota').sum());sets_w=int(ps['Venceu'].sum());sets_l=int((~ps['Venceu']).sum());ct,cn,max_w,max_l=streak_data(pm['Resultado'].tolist())
    st.markdown(f'<div class="hero-kicker">Análise do jogador</div><div class="hero-title">{html.escape(selected)}</div><div class="hero-sub">Histórico completo, sequência, desempenho por set e padrões automáticos.</div>',unsafe_allow_html=True)
    m=st.columns(8);m[0].metric('Jogos',len(pm),'100% da base');m[1].metric('Vitórias',wins,f'{pct(wins,len(pm)):.1%}');m[2].metric('Derrotas',losses,f'{pct(losses,len(pm)):.1%}');m[3].metric('Sets (V/D)',f'{sets_w} / {sets_l}',f'{sets_w-sets_l:+d}');m[4].metric('Aproveitamento',f'{pct(wins,len(pm)):.1%}');m[5].metric('Sequência atual',cn,'Vitória' if ct=='V' else 'Derrota');m[6].metric('Melhor sequência',max_w,'Vitórias');m[7].metric('Pior sequência',max_l,'Derrotas')
    left,right=st.columns([1.42,1],gap='medium')
    with left:
        tabs=st.tabs([f'Histórico de partidas ({len(pm)})','Resumo','Desempenho','Análises','Gráficos'])
        with tabs[0]:
            a,b=st.columns(2);order=a.selectbox('Ordenação',['Mais recentes','Mais antigas']);rf=b.selectbox('Resultado',['Todos','Vitórias','Derrotas']);hist=pm.copy()
            if rf=='Vitórias':hist=hist[hist['Resultado']=='Vitória']
            elif rf=='Derrotas':hist=hist[hist['Resultado']=='Derrota']
            hist=hist.sort_values(['Data','Horário','Ordem Entrada'],ascending=(order=='Mais antigas'));show=hist.head(10);st.markdown(history_html(show,selected),unsafe_allow_html=True);st.caption(f'Mostrando 1 a {min(10,len(hist))} de {len(hist)}')
        with tabs[1]:
            st.write(f'**Jogos:** {len(pm)}');st.write(f'**Vitórias:** {wins}');st.write(f'**Derrotas:** {losses}');st.write(f'**Aproveitamento:** {pct(wins,len(pm)):.1%}');st.write(f"**Média de pontos feitos:** {pm['Pontos Feitos'].mean():.1f}");st.write(f"**Média de pontos sofridos:** {pm['Pontos Sofridos'].mean():.1f}")
        with tabs[2]:st.dataframe(ss.style.format({'Aproveitamento':'{:.1%}','Média_feitos':'{:.1f}','Média_sofridos':'{:.1f}'}),use_container_width=True,hide_index=True)
        with tabs[3]:
            best=ss.sort_values(['Aproveitamento','Vitórias'],ascending=False).iloc[0];worst=ss.sort_values(['Aproveitamento','Vitórias']).iloc[0]
            st.markdown(f'<div class="analysis-box"><div class="analysis-title">🧠 Análise automática</div><div class="analysis-text">O melhor desempenho de <b>{html.escape(selected)}</b> ocorre no <b>{int(best["Nº Set"])}º set</b>, com {best["Aproveitamento"]:.1%}. O pior ocorre no <b>{int(worst["Nº Set"])}º set</b>, com {worst["Aproveitamento"]:.1%}.</div></div>',unsafe_allow_html=True)
        with tabs[4]:
            st.line_chart(pd.Series([1 if x=='Vitória' else 0 for x in pm['Resultado']],name='Forma'))
    with right:
        r1,r2=st.columns([.9,1.1],gap='small')
        with r1:st.markdown(f'<div class="panel"><div class="panel-title">Forma atual</div><div class="panel-sub">Últimos 10 jogos</div>{form_html(pm)}<div style="margin-top:10px;color:#91A4BC;font-size:.8rem">Sequência atual: <b style="color:#FFF">{cn} {"vitória" if ct=="V" else "derrota"}</b></div>{spark_html(pm)}</div>',unsafe_allow_html=True)
        with r2:st.markdown(sets_html(ss),unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True);st.markdown(scorelines_html(pm),unsafe_allow_html=True);st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True);st.markdown(first_set_html(fs),unsafe_allow_html=True)
        best=ss.sort_values(['Aproveitamento','Vitórias'],ascending=False).iloc[0];worst=ss.sort_values(['Aproveitamento','Vitórias']).iloc[0]
        text=f"{selected} tem melhor rendimento no {int(best['Nº Set'])}º set ({best['Aproveitamento']:.1%}). Seu pior rendimento ocorre no {int(worst['Nº Set'])}º set ({worst['Aproveitamento']:.1%}). Quando vence o primeiro set, ganha a partida em {pct(fs['confirmed'],fs['won_first']):.1%} das vezes."
        st.markdown('<div style="height:12px"></div>',unsafe_allow_html=True);st.markdown(f'<div class="analysis-box"><div class="analysis-title">🧠 Análise automática</div><div class="analysis-text">{html.escape(text)}</div></div>',unsafe_allow_html=True)
elif page=='Confrontos (H2H)':
    a,b=st.columns(2);p1=a.selectbox('Jogador 1',nomes);p2=b.selectbox('Jogador 2',[n for n in nomes if n!=p1]);df=partidas[((partidas['Jogador 1']==p1)&(partidas['Jogador 2']==p2))|((partidas['Jogador 1']==p2)&(partidas['Jogador 2']==p1))].copy();st.dataframe(df,use_container_width=True,hide_index=True) if not df.empty else st.warning('Não existem confrontos registrados.')
elif page=='Desempenho por Set':
    n=st.selectbox('Jogador',nomes);ss=set_summary(n);st.markdown(sets_html(ss),unsafe_allow_html=True);st.dataframe(ss,use_container_width=True,hide_index=True)
elif page=='Sequências':
    rows=[]
    for n in nomes:
        pm=player_matches(n);t,c,mw,ml=streak_data(pm['Resultado'].tolist());rows.append({'Jogador':n,'Sequência atual':f'{c} {"V" if t=="V" else "D"}','Maior sequência de vitórias':mw,'Maior sequência de derrotas':ml})
    st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
elif page=='Horários':
    n=st.selectbox('Jogador',nomes);pm=player_matches(n);pm['Hora']=pd.to_datetime(pm['Horário'],format='%H:%M',errors='coerce').dt.hour;tab=pm.groupby('Hora').agg(Jogos=('Resultado','size'),Vitórias=('Resultado',lambda x:(x=='Vitória').sum())).reset_index();tab['Aproveitamento']=tab['Vitórias']/tab['Jogos'];st.dataframe(tab.style.format({'Aproveitamento':'{:.1%}'}),use_container_width=True,hide_index=True)
elif page=='Dias da Semana':
    n=st.selectbox('Jogador',nomes);pm=player_matches(n);dias={0:'Segunda',1:'Terça',2:'Quarta',3:'Quinta',4:'Sexta',5:'Sábado',6:'Domingo'};pm['Dia']=pm['Data'].dt.dayofweek.map(dias);tab=pm.groupby('Dia').agg(Jogos=('Resultado','size'),Vitórias=('Resultado',lambda x:(x=='Vitória').sum())).reset_index();tab['Aproveitamento']=tab['Vitórias']/tab['Jogos'];st.dataframe(tab.style.format({'Aproveitamento':'{:.1%}'}),use_container_width=True,hide_index=True)
elif page=='Placares':
    n=st.selectbox('Jogador',nomes);st.markdown(scorelines_html(player_matches(n)),unsafe_allow_html=True)
elif page=='Viradas':
    n=st.selectbox('Jogador',nomes);st.markdown(first_set_html(first_set_stats(n)),unsafe_allow_html=True)
elif page=='Rankings':
    rows=[]
    for n in nomes:
        pm=player_matches(n);w=int((pm['Resultado']=='Vitória').sum());rows.append({'Jogador':n,'Jogos':len(pm),'Vitórias':w,'Derrotas':len(pm)-w,'Aproveitamento':pct(w,len(pm)),'Média de pontos':pm['Pontos Feitos'].mean()})
    st.dataframe(pd.DataFrame(rows).sort_values(['Aproveitamento','Vitórias'],ascending=False).style.format({'Aproveitamento':'{:.1%}','Média de pontos':'{:.1f}'}),use_container_width=True,hide_index=True)
elif page in ['Jogos do Dia','Pergunte ao Banco','Relatórios','Configurações']:
    st.info('Área mantida no menu conforme o layout aprovado. A funcionalidade será aprofundada na próxima atualização.')
else:
    t1,t2=st.tabs(['Partidas','Sets'])
    with t1:st.dataframe(partidas,use_container_width=True,hide_index=True)
    with t2:st.dataframe(sets,use_container_width=True,hide_index=True)
