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
.block-container{max-width:1700px;padding-top:1rem;padding-bottom:2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#050D18,#071321);border-right:1px solid #17283D}
[data-testid="stSidebar"] *{color:#EAF1FB}
h1,h2,h3,h4,p,label,span{color:var(--text)}
div[data-testid="stMetric"]{background:linear-gradient(180deg,#0E1D30,#0A1524);border:1px solid #1D334D;padding:14px 16px;border-radius:13px;min-height:116px;box-shadow:0 12px 30px rgba(0,0,0,.24)}
div[data-testid="stMetricLabel"]{color:#B5C3D5;font-size:.77rem;text-transform:uppercase}
div[data-testid="stMetricValue"]{color:#FFF;font-weight:850}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div{background:#0B1625!important;border:1px solid #28415E!important;border-radius:10px!important;color:white!important}input{color:white!important}
.hero-kicker{color:#B7C4D4;font-size:.85rem;font-weight:800;text-transform:uppercase;letter-spacing:.04em}.hero-title{font-size:2rem;line-height:1.05;font-weight:900;color:#FFF}.hero-sub{color:#91A4BC;margin-top:.35rem}
.panel{background:linear-gradient(180deg,#0D1929,#091421);border:1px solid #1D334D;border-radius:14px;padding:15px;box-shadow:0 12px 28px rgba(0,0,0,.20);height:100%}.panel-title{font-weight:850;color:#F8FAFC;font-size:.94rem;text-transform:uppercase;margin-bottom:12px}.panel-sub{color:#8296AE;font-size:.78rem;margin-top:-7px;margin-bottom:10px}
.history-wrap{background:linear-gradient(180deg,#0C1828,#09131F);border:1px solid #1D334D;border-radius:14px;overflow:hidden}.history-head{display:grid;grid-template-columns:120px 86px minmax(210px,1fr) 88px 90px 34px;gap:10px;padding:13px 16px;color:#91A4BC;font-size:.72rem;font-weight:800;text-transform:uppercase;border-bottom:1px solid #1D3047}.match-row{display:grid;grid-template-columns:120px 86px minmax(210px,1fr) 88px 90px 34px;gap:10px;align-items:center;padding:12px 16px;border-bottom:1px solid #182A3E}.match-row:hover{background:#101F32}.match-date,.match-time{color:#E6EEF8;font-size:.9rem}.opponent{color:#FFF;font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.avatar{display:inline-flex;width:25px;height:25px;border-radius:50%;align-items:center;justify-content:center;margin-right:8px;background:#1E4E8C;color:#FFF;font-size:.72rem}.score{color:#FFF;font-weight:850;font-size:1rem;text-align:center}.result-badge{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#FFF;font-weight:900;margin:auto}.result-win{background:linear-gradient(180deg,#22A447,#14843A)}.result-loss{background:linear-gradient(180deg,#EF3F3F,#BE2020)}.arrow{color:#6D86A3;font-size:1.2rem;text-align:right}
.form-strip{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 4px}.form-dot{width:25px;height:25px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:900;color:white}.form-win{background:#178C45}.form-loss{background:#CF2D2D}
.set-row{display:grid;grid-template-columns:62px 1fr 48px 48px 54px 84px;align-items:center;gap:8px;padding:9px 0;border-bottom:1px solid #182B40}.set-row:last-child{border-bottom:none}.set-name{font-weight:800;color:#FFF}.set-num,.set-pct,.set-avg{color:#EAF1FB;font-size:.84rem;text-align:center}.progress{height:5px;border-radius:99px;background:#17273A;overflow:hidden;margin-top:5px}.progress>span{display:block;height:100%;border-radius:99px}
.score-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.score-column{background:#0A1522;border:1px solid #1B3048;border-radius:10px;padding:12px}.score-title{font-size:.74rem;font-weight:900;text-transform:uppercase;margin-bottom:8px}.score-line{display:grid;grid-template-columns:42px 1fr 38px;gap:8px;align-items:center;margin:9px 0}.score-label{font-weight:850;color:#FFF}.score-count{color:#B7C6D8;text-align:right;font-size:.82rem}.mini-bar{height:5px;border-radius:99px;background:#182A3E;overflow:hidden}.mini-bar span{display:block;height:100%;border-radius:99px}
.first-card{border-radius:12px;padding:15px;border:1px solid #24405D;background:#0A1624}.first-card.good{background:linear-gradient(180deg,#10271D,#0B1B16);border-color:#214C35}.first-card.bad{background:linear-gradient(180deg,#2B1619,#1B1014);border-color:#4B2329}.first-icon{width:42px;height:42px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:1.15rem;font-weight:900;float:left;margin-right:12px}.first-value{font-size:1.55rem;font-weight:900;color:#FFF}.first-label{font-size:.78rem;font-weight:850;color:#EAF1FB;text-transform:uppercase}.first-sub{font-size:.78rem;color:#91A4BC;margin-top:3px}
.analysis-box{border-radius:12px;border:1px solid #6D4AFF;background:linear-gradient(135deg,rgba(50,29,103,.34),rgba(10,20,35,.96));padding:16px}.analysis-title{font-weight:900;color:#FFF;margin-bottom:7px}.analysis-text{color:#C7D3E2;line-height:1.5}
.stTabs [data-baseweb="tab"]{background:#0B1625;border:1px solid #1D334D;color:#A6B8CD;border-radius:8px 8px 0 0}.stTabs [aria-selected="true"]{background:#21165A!important;color:#FFF!important;border-color:#6D4AFF!important}
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

def history_html(df):
    if df.empty:return '<div class="panel">Nenhuma partida encontrada.</div>'
    rows=[]
    for _,r in df.iterrows():
        cls='result-win' if r['Resultado']=='Vitória' else 'result-loss';letter='V' if r['Resultado']=='Vitória' else 'D';date=r['Data'].strftime('%d/%m/%Y') if pd.notna(r['Data']) else '-'
        rows.append(f'''<div class="match-row"><div class="match-date">{date}</div><div class="match-time">{html.escape(str(r['Horário']))}</div><div class="opponent"><span class="avatar">{html.escape(initials(r['Adversário']))}</span>{html.escape(str(r['Adversário']))}</div><div class="score">{html.escape(str(r['Placar']))}</div><div><div class="result-badge {cls}">{letter}</div></div><div class="arrow">›</div></div>''')
    return '<div class="history-wrap"><div class="history-head"><div>Data</div><div>Hora</div><div>Adversário</div><div>Placar</div><div>Resultado</div><div></div></div>'+''.join(rows)+'</div>'

def form_html(df,limit=10):
    recent=df.sort_values(['Data','Horário','Ordem Entrada'],ascending=False).head(limit);dots=[]
    for _,r in recent.iloc[::-1].iterrows():
        cls='form-win' if r['Resultado']=='Vitória' else 'form-loss';letter='V' if r['Resultado']=='Vitória' else 'D';dots.append(f'<span class="form-dot {cls}">{letter}</span>')
    return '<div class="form-strip">'+''.join(dots)+'</div>'

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
page=st.sidebar.radio('Menu',['Dashboard','Jogadores','Confrontos (H2H)','Desempenho por Set','Sequências','Horários','Dias da Semana','Placares','Viradas','Rankings','Base de Dados'],label_visibility='collapsed')
st.sidebar.markdown('---');st.sidebar.markdown('#### BASE DE DADOS');st.sidebar.write(f'Partidas: **{len(partidas)}**');st.sidebar.write(f'Sets: **{len(sets)}**');st.sidebar.write(f'Jogadores: **{len(nomes)}**');st.sidebar.caption('● Base oficial ativa')

if page in ['Dashboard','Jogadores']:
    selected=st.selectbox('Selecionar jogador',nomes,index=0);pm=player_matches(selected);ps=player_sets(selected);ss=set_summary(selected);fs=first_set_stats(selected)
    wins=int((pm['Resultado']=='Vitória').sum());losses=int((pm['Resultado']=='Derrota').sum());sets_w=int(ps['Venceu'].sum());sets_l=int((~ps['Venceu']).sum());ct,cn,max_w,max_l=streak_data(pm['Resultado'].tolist())
    st.markdown(f'<div class="hero-kicker">Análise do jogador</div><div class="hero-title">{html.escape(selected)}</div><div class="hero-sub">Histórico completo, sequência, desempenho por set e padrões automáticos.</div>',unsafe_allow_html=True)
    c1,c2,c3,c4,c5,c6,c7,c8=st.columns(8);c1.metric('Jogos',len(pm));c2.metric('Vitórias',wins,f'{pct(wins,len(pm)):.1%}');c3.metric('Derrotas',losses,f'{pct(losses,len(pm)):.1%}');c4.metric('Sets (V/D)',f'{sets_w} / {sets_l}',f'saldo {sets_w-sets_l:+d}');c5.metric('Aproveitamento',f'{pct(wins,len(pm)):.1%}');c6.metric('Sequência atual',cn,'Vitórias' if ct=='V' else 'Derrotas');c7.metric('Melhor sequência',max_w,'Vitórias');c8.metric('Pior sequência',max_l,'Derrotas')
    left,right=st.columns([1.35,1])
    with left:
        tabs=st.tabs(['Histórico de partidas','Resumo','Desempenho','Análises'])
        with tabs[0]:
            a,b=st.columns(2);order=a.selectbox('Ordenação',['Mais recentes','Mais antigas']);rf=b.selectbox('Resultado',['Todos','Vitórias','Derrotas']);hist=pm.copy()
            if rf=='Vitórias':hist=hist[hist['Resultado']=='Vitória']
            elif rf=='Derrotas':hist=hist[hist['Resultado']=='Derrota']
            hist=hist.sort_values(['Data','Horário','Ordem Entrada'],ascending=(order=='Mais antigas'));st.markdown(history_html(hist),unsafe_allow_html=True)
        with tabs[1]:
            st.write(f'**Jogos:** {len(pm)}');st.write(f'**Vitórias:** {wins}');st.write(f'**Derrotas:** {losses}');st.write(f'**Aproveitamento:** {pct(wins,len(pm)):.1%}');st.write(f"**Média de pontos feitos:** {pm['Pontos Feitos'].mean():.1f}");st.write(f"**Média de pontos sofridos:** {pm['Pontos Sofridos'].mean():.1f}")
        with tabs[2]:st.dataframe(ss.style.format({'Aproveitamento':'{:.1%}','Média_feitos':'{:.1f}','Média_sofridos':'{:.1f}'}),use_container_width=True,hide_index=True)
        with tabs[3]:
            best=ss.sort_values(['Aproveitamento','Vitórias'],ascending=False).iloc[0];worst=ss.sort_values(['Aproveitamento','Vitórias']).iloc[0]
            st.markdown(f'<div class="analysis-box"><div class="analysis-title">🧠 Análise automática</div><div class="analysis-text">O melhor desempenho de <b>{html.escape(selected)}</b> ocorre no <b>{int(best["Nº Set"])}º set</b>, com {best["Aproveitamento"]:.1%}. O pior ocorre no <b>{int(worst["Nº Set"])}º set</b>, com {worst["Aproveitamento"]:.1%}.</div></div>',unsafe_allow_html=True)
    with right:
        r1,r2=st.columns([.82,1.18])
        with r1:st.markdown(f'<div class="panel"><div class="panel-title">Forma atual</div><div class="panel-sub">Últimos 10 jogos</div>{form_html(pm)}<div style="margin-top:12px;color:#91A4BC;font-size:.8rem">Sequência atual: <b style="color:#FFF">{cn} {"vitórias" if ct=="V" else "derrotas"}</b></div></div>',unsafe_allow_html=True)
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
else:
    t1,t2=st.tabs(['Partidas','Sets'])
    with t1:st.dataframe(partidas,use_container_width=True,hide_index=True)
    with t2:st.dataframe(sets,use_container_width=True,hide_index=True)
