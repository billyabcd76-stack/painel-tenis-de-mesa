from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Inteligência do Tênis de Mesa — V2.0",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root{
      --bg:#06101d;--panel:#0c1a2b;--panel2:#101f32;--line:#2b3e56;
      --text:#f7f9fc;--muted:#a9b7c9;--green:#35d05b;--red:#ff3b4e;
      --yellow:#ffb31a;--purple:#9d52ff;--pink:#ff3f8f;--blue:#5fa8ff;
    }
    html,body,[data-testid="stAppViewContainer"],.stApp{background:var(--bg)!important;color:var(--text)!important}
    [data-testid="stHeader"]{background:rgba(6,16,29,.96)!important}
    .block-container{padding-top:1.25rem!important;padding-bottom:2rem!important;max-width:1500px!important}
    .stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp p,.stApp span,.stApp label{color:var(--text)!important;opacity:1!important}
    [data-testid="stCaptionContainer"] p{color:var(--muted)!important}

    section[data-testid="stSidebar"]{background:#081525!important;border-right:1px solid #243850!important}
    section[data-testid="stSidebar"] *{color:#fff!important;opacity:1!important}
    section[data-testid="stSidebar"] div[role="radiogroup"]>label{background:transparent!important;border:1px solid transparent!important;border-radius:10px!important;padding:11px 12px!important;margin:4px 0!important}
    section[data-testid="stSidebar"] div[role="radiogroup"]>label p{font-size:.96rem!important;font-weight:800!important}
    section[data-testid="stSidebar"] div[role="radiogroup"]>label:hover{background:#10233a!important;border-color:#33516f!important}
    section[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked){background:linear-gradient(90deg,#c7195e,#67359b)!important;border-color:#ff4f9b!important}
    .sidebar-brand{font-size:1.05rem;font-weight:900;letter-spacing:.02em;margin:4px 0 10px}
    .sidebar-kicker{font-size:.72rem;color:#92a6bd!important;text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px}
    .db-card{margin-top:22px;background:#0b1a2c;border:1px solid #2a4059;border-radius:12px;padding:14px}
    .db-card b{font-size:.95rem}.db-num{font-size:1.55rem;font-weight:900}.db-time{color:var(--green)!important;font-weight:900}

    .hero{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:12px}
    .hero-title{font-size:2.05rem;font-weight:900;letter-spacing:-.02em}.hero-sub{color:var(--muted)!important;margin-top:2px}
    .statusbar{background:#0a1b30;border:1px solid #35577b;border-radius:10px;padding:11px 14px;margin:10px 0 18px;font-weight:700}
    .section-kicker{color:var(--pink)!important;font-weight:900;font-size:1.05rem;text-transform:uppercase;letter-spacing:.03em;margin:8px 0 2px}
    .section-sub{color:var(--muted)!important;margin-bottom:12px}

    [data-baseweb="select"]>div{background:#102238!important;border:1px solid #2b425d!important;color:#fff!important;min-height:46px!important}
    [data-baseweb="select"] *{color:#fff!important}
    [data-baseweb="popover"] *{color:#111!important}
    .vs{display:flex;align-items:center;justify-content:center;font-weight:900;font-size:2rem;height:46px}

    .metric-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px;margin:14px 0}
    .metric-card{background:linear-gradient(180deg,#102139,#0b1829);border:1px solid #334a64;border-radius:11px;padding:14px 16px;min-height:105px}
    .metric-label{font-size:.78rem;font-weight:900;text-transform:uppercase;color:#dbe5f0!important}.metric-value{font-size:2.15rem;font-weight:900;line-height:1.05;margin-top:6px}.metric-sub{font-size:.86rem;color:#dce5f0!important;margin-top:4px;font-weight:700}
    .green{color:var(--green)!important}.red{color:var(--red)!important}.yellow{color:var(--yellow)!important}.purple{color:var(--purple)!important}.pink{color:var(--pink)!important}.blue{color:var(--blue)!important}

    .player-card{background:#0b192b;border:1px solid #2d425a;border-radius:11px;padding:14px 16px;margin:4px 0 10px}.player-card.green-border{border-top:3px solid var(--green)}.player-card.red-border{border-top:3px solid var(--red)}
    .player-title{font-weight:900;font-size:1.05rem}.player-grid{display:grid;grid-template-columns:1.25fr 1fr;gap:8px 24px;margin-top:10px}.rowline{display:flex;justify-content:space-between;border-bottom:1px solid #20334a;padding:6px 0}.rowline:last-child{border-bottom:none}.value-strong{font-weight:900}

    .results-card{background:#0b192b;border:1px solid #2d425a;border-radius:10px;padding:12px 14px;margin:8px 0}.results-title{font-size:.78rem;font-weight:900;text-transform:uppercase;margin-bottom:9px}.result-badge{display:inline-flex;align-items:center;justify-content:center;width:28px;height:28px;border-radius:5px;font-weight:900;margin-right:5px;color:#fff!important}.v{background:#198b36}.d{background:#b82334}

    .insight{background:#0b192b;border:1px solid #2e455f;border-left:5px solid var(--blue);border-radius:10px;padding:12px 14px;margin:8px 0;font-weight:750}.insight.ok{border-left-color:var(--green)}.insight.warn{border-left-color:var(--yellow)}

    [data-testid="stDataFrame"], [data-testid="stTable"]{border:1px solid #2d425a!important;border-radius:10px!important;overflow:hidden!important}
    [data-testid="stDataFrame"] *{opacity:1!important}
    div[data-testid="stMetric"]{background:#0b192b!important;border:1px solid #2d425a!important;border-radius:10px!important;padding:12px!important}
    div[data-testid="stMetric"] [data-testid="stMetricValue"]{color:#fff!important;font-weight:900!important}

    @media(max-width:900px){.metric-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.hero{display:block}.player-grid{grid-template-columns:1fr}}
    </style>
    """, unsafe_allow_html=True)

DIAS_PT = {
    0: "Segunda-feira",
    1: "Terça-feira",
    2: "Quarta-feira",
    3: "Quinta-feira",
    4: "Sexta-feira",
    5: "Sábado",
    6: "Domingo",
}


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    caminho = Path(__file__).parent / "partidas.csv"
    df = pd.read_csv(caminho, encoding="utf-8-sig")

    obrigatorias = {
        "id", "data", "hora", "jogador_1", "jogador_2", "sets_j1", "sets_j2"
    }
    ausentes = obrigatorias.difference(df.columns)
    if ausentes:
        raise ValueError(f"Colunas ausentes no arquivo: {', '.join(sorted(ausentes))}")

    df["data_hora"] = pd.to_datetime(
        df["data"].astype(str) + " " + df["hora"].astype(str), errors="coerce"
    )
    df = df.dropna(subset=["data_hora"]).copy()
    df["data"] = df["data_hora"].dt.date
    df["hora_num"] = df["data_hora"].dt.hour
    df["dia_semana_calc"] = df["data_hora"].dt.dayofweek.map(DIAS_PT)
    df["vencedor"] = df.apply(
        lambda r: r["jogador_1"] if r["sets_j1"] > r["sets_j2"] else r["jogador_2"],
        axis=1,
    )
    return df.sort_values(["data_hora", "id"]).reset_index(drop=True)


def criar_registros(df: pd.DataFrame) -> pd.DataFrame:
    registros: list[dict] = []
    for _, r in df.iterrows():
        j1_venceu = r["sets_j1"] > r["sets_j2"]
        base = {
            "id": r["id"],
            "data_hora": r["data_hora"],
            "data": r["data"],
            "dia_semana": r["dia_semana_calc"],
            "hora_num": r["hora_num"],
            "total_sets": int(r["sets_j1"] + r["sets_j2"]),
        }
        registros.append(
            {
                **base,
                "jogador": r["jogador_1"],
                "adversario": r["jogador_2"],
                "sets_pro": int(r["sets_j1"]),
                "sets_contra": int(r["sets_j2"]),
                "resultado": "V" if j1_venceu else "D",
            }
        )
        registros.append(
            {
                **base,
                "jogador": r["jogador_2"],
                "adversario": r["jogador_1"],
                "sets_pro": int(r["sets_j2"]),
                "sets_contra": int(r["sets_j1"]),
                "resultado": "V" if not j1_venceu else "D",
            }
        )

    reg = pd.DataFrame(registros).sort_values(["data_hora", "id"]).reset_index(drop=True)
    reg["ordem_no_dia"] = reg.groupby(["jogador", "data"]).cumcount() + 1
    return reg


def sequencias(resultados: list[str]) -> tuple[int, int, str, int]:
    if not resultados:
        return 0, 0, "—", 0

    maior_v = maior_d = atual_v = atual_d = 0
    for resultado in resultados:
        if resultado == "V":
            atual_v += 1
            atual_d = 0
        else:
            atual_d += 1
            atual_v = 0
        maior_v = max(maior_v, atual_v)
        maior_d = max(maior_d, atual_d)

    ultimo = resultados[-1]
    tamanho = 0
    for resultado in reversed(resultados):
        if resultado != ultimo:
            break
        tamanho += 1
    texto = f"{'Vitórias' if ultimo == 'V' else 'Derrotas'} ({tamanho})"
    return maior_v, maior_d, texto, tamanho


def formatar_tempo(delta: pd.Timedelta | None) -> str:
    if delta is None or pd.isna(delta):
        return "—"
    minutos = int(delta.total_seconds() // 60)
    if minutos < 60:
        return f"{minutos} min"
    horas = minutos // 60
    resto = minutos % 60
    if horas < 24:
        return f"{horas}h {resto:02d}min"
    dias = horas // 24
    return f"{dias} dia{'s' if dias != 1 else ''}"


def dados_jogador(reg: pd.DataFrame, jogador: str) -> pd.DataFrame:
    return reg[reg["jogador"] == jogador].sort_values(["data_hora", "id"]).copy()


def resumo_jogador(reg: pd.DataFrame, jogador: str) -> dict:
    d = dados_jogador(reg, jogador)
    jogos = len(d)
    vitorias = int((d["resultado"] == "V").sum())
    maior_v, maior_d, seq_texto, seq_tamanho = sequencias(d["resultado"].tolist())
    return {
        "jogos": jogos,
        "vitorias": vitorias,
        "derrotas": jogos - vitorias,
        "aproveitamento": (vitorias / jogos * 100) if jogos else 0,
        "maior_v": maior_v,
        "maior_d": maior_d,
        "sequencia": seq_texto,
        "sequencia_tamanho": seq_tamanho,
        "ultima": d["data_hora"].max() if jogos else None,
    }


def padrao_intervalos(d: pd.DataFrame) -> dict:
    dias_ativos = sorted(pd.Series(d["data"].unique()).tolist())
    if len(dias_ativos) < 2:
        return {
            "dias_ativos": len(dias_ativos),
            "intervalos": [],
            "media": None,
            "moda": None,
            "regularidade": None,
        }
    datas = pd.to_datetime(pd.Series(dias_ativos))
    intervalos = datas.diff().dt.days.dropna().astype(int).tolist()
    contagem = Counter(intervalos)
    moda, repeticoes = contagem.most_common(1)[0]
    regularidade = repeticoes / len(intervalos) * 100
    return {
        "dias_ativos": len(dias_ativos),
        "intervalos": intervalos,
        "media": sum(intervalos) / len(intervalos),
        "moda": moda,
        "regularidade": regularidade,
    }


def faixa_horaria(hora: int) -> str:
    if hora < 6:
        return "Madrugada"
    if hora < 12:
        return "Manhã"
    if hora < 18:
        return "Tarde"
    return "Noite"


def gerar_insights_jogador(d: pd.DataFrame) -> list[tuple[str, str]]:
    insights: list[tuple[str, str]] = []
    if d.empty:
        return insights

    por_dia = d.groupby("data").size()
    if len(por_dia) >= 3:
        media = por_dia.mean()
        mediana = por_dia.median()
        minimo = int(por_dia.min())
        maximo = int(por_dia.max())
        insights.append(
            ("ok", f"Volume: média de {media:.1f} partidas por dia ativo; faixa observada de {minimo} a {maximo}.")
        )
        if mediana >= 8:
            insights.append(("ok", f"Joga em alto volume: mediana de {mediana:.0f} partidas por dia ativo."))
    else:
        insights.append(("warn", "Volume diário ainda sem histórico suficiente: são necessários pelo menos 3 dias ativos."))

    p = padrao_intervalos(d)
    if len(p["intervalos"]) >= 3:
        if p["regularidade"] >= 60:
            insights.append(
                ("ok", f"Padrão de retorno: intervalo de {p['moda']} dias ocorreu em {p['regularidade']:.0f}% dos intervalos.")
            )
        else:
            insights.append(("warn", "Os intervalos entre aparições ainda são irregulares."))
    else:
        insights.append(("warn", "Frequência entre dias ainda sem dados suficientes para definir um ciclo."))

    if len(d) >= 8:
        por_ordem = d.groupby("ordem_no_dia")["resultado"].apply(lambda s: (s == "V").mean() * 100)
        inicio = por_ordem[por_ordem.index <= 3].mean() if any(por_ordem.index <= 3) else None
        fim = por_ordem[por_ordem.index >= 6].mean() if any(por_ordem.index >= 6) else None
        if inicio is not None and fim is not None and not pd.isna(fim):
            diferenca = fim - inicio
            if diferenca <= -15:
                insights.append(("ok", f"Possível desgaste: aproveitamento após a 6ª partida cai {abs(diferenca):.0f} pontos percentuais."))
            elif diferenca >= 15:
                insights.append(("ok", f"Cresce com o volume: após a 6ª partida, o aproveitamento sobe {diferenca:.0f} pontos percentuais."))

    horario = d["hora_num"].map(faixa_horaria).value_counts(normalize=True)
    if not horario.empty and horario.iloc[0] >= 0.55:
        insights.append(("ok", f"Horário predominante: {horario.index[0]} concentra {horario.iloc[0] * 100:.0f}% das partidas."))

    return insights


def ultima_situacao_jogador(d: pd.DataFrame, fechamento: pd.Timestamp) -> dict:
    if d.empty:
        return {
            "ultima": None, "jogos_ultimo_dia": 0, "vitorias_ultimo_dia": 0,
            "derrotas_ultimo_dia": 0, "tempo_sem_registro": None, "confianca": "Sem dados"
        }
    ultima = d["data_hora"].max()
    ultimo_dia = d["data"].max()
    recorte = d[d["data"] == ultimo_dia]
    delta = fechamento - ultima
    horas = delta.total_seconds() / 3600
    if horas < 24:
        confianca = "Baixa — banco pode estar incompleto nas últimas 24h"
    elif horas < 72:
        confianca = "Moderada"
    else:
        confianca = "Alta"
    return {
        "ultima": ultima,
        "jogos_ultimo_dia": len(recorte),
        "vitorias_ultimo_dia": int((recorte["resultado"] == "V").sum()),
        "derrotas_ultimo_dia": int((recorte["resultado"] == "D").sum()),
        "tempo_sem_registro": delta,
        "confianca": confianca,
    }


def resumo_confronto(confrontos: pd.DataFrame, jogador_a: str, jogador_b: str) -> dict:
    total = len(confrontos)
    vit_a = int((confrontos["vencedor"] == jogador_a).sum())
    vit_b = int((confrontos["vencedor"] == jogador_b).sum())
    pct_a = vit_a / total * 100 if total else 0
    pct_b = vit_b / total * 100 if total else 0
    equilibrio = abs(pct_a - pct_b)
    if total == 0:
        classificacao = "Sem histórico"
    elif equilibrio <= 10:
        classificacao = "Muito equilibrado"
    elif equilibrio <= 25:
        classificacao = "Equilibrado"
    else:
        classificacao = "Vantagem clara no histórico"
    jogos_5_sets = int(((confrontos["sets_j1"] + confrontos["sets_j2"]) == 5).sum()) if total else 0
    return {
        "total": total, "vit_a": vit_a, "vit_b": vit_b,
        "pct_a": pct_a, "pct_b": pct_b, "classificacao": classificacao,
        "jogos_5_sets": jogos_5_sets,
        "pct_5_sets": jogos_5_sets / total * 100 if total else 0,
    }


def ultimos_resultados_confronto(confrontos: pd.DataFrame, jogador: str, limite: int = 10) -> str:
    if confrontos.empty:
        return "—"
    ultimos = confrontos.sort_values(["data_hora", "id"]).tail(limite)
    return " ".join("V" if vencedor == jogador else "D" for vencedor in ultimos["vencedor"])


def insights_confronto(confrontos: pd.DataFrame, jogador_a: str, jogador_b: str) -> list[tuple[str, str]]:
    r = resumo_confronto(confrontos, jogador_a, jogador_b)
    saida: list[tuple[str, str]] = []
    if r["total"] == 0:
        return [("warn", "Ainda não há confronto direto registrado entre os jogadores.")]
    if r["total"] < 5:
        saida.append(("warn", f"Amostra pequena: apenas {r['total']} confronto(s). Evite tratar a vantagem atual como padrão consolidado."))
    else:
        lider = jogador_a if r["vit_a"] > r["vit_b"] else jogador_b if r["vit_b"] > r["vit_a"] else None
        if lider:
            vantagem = abs(r["pct_a"] - r["pct_b"])
            saida.append(("ok", f"{lider} lidera o histórico; diferença de {vantagem:.1f} pontos percentuais entre os aproveitamentos diretos."))
        else:
            saida.append(("ok", "O histórico direto está empatado."))
    if r["pct_5_sets"] >= 40 and r["total"] >= 5:
        saida.append(("ok", f"Confronto longo: {r['pct_5_sets']:.0f}% das partidas chegaram ao 5º set."))
    elif r["total"] >= 5:
        saida.append(("ok", f"Partidas de 5 sets representam {r['pct_5_sets']:.0f}% do confronto."))
    por_dia = confrontos.groupby("data").size()
    if len(por_dia) >= 2:
        saida.append(("ok", f"Quando se encontram, disputam em média {por_dia.mean():.1f} partida(s) no mesmo dia; máximo observado de {int(por_dia.max())}."))
    else:
        saida.append(("warn", "O banco possui somente um dia desse confronto; ainda não é possível definir frequência entre aparições."))
    return saida


def tabela_historico(d: pd.DataFrame) -> pd.DataFrame:
    h = d.sort_values(["data_hora", "id"], ascending=False).copy()
    h["Data"] = h["data_hora"].dt.strftime("%d/%m/%Y")
    h["Hora"] = h["data_hora"].dt.strftime("%H:%M")
    h["Placar"] = h["sets_pro"].astype(str) + " x " + h["sets_contra"].astype(str)
    h["Resultado"] = h["resultado"].map({"V": "Vitória", "D": "Derrota"})
    return h[["Data", "Hora", "ordem_no_dia", "adversario", "Placar", "Resultado"]].rename(
        columns={"ordem_no_dia": "Partida do dia", "adversario": "Adversário"}
    )




def esc(text: object) -> str:
    import html
    return html.escape(str(text))


def result_badges(values: list[str]) -> str:
    if not values:
        return "<span style='color:#9fb0c3'>Sem dados</span>"
    return "".join(f"<span class='result-badge {'v' if x=='V' else 'd'}'>{x}</span>" for x in values)


def metric_card(label: str, value: object, sub: str = "", color: str = "") -> str:
    return f"<div class='metric-card'><div class='metric-label'>{esc(label)}</div><div class='metric-value {color}'>{esc(value)}</div><div class='metric-sub'>{esc(sub)}</div></div>"


def player_panel(nome: str, resumo: dict, situacao: dict, color: str) -> str:
    seq_cor = "green" if resumo['sequencia'].startswith('Vitórias') else "red"
    return f"""
    <div class='player-card {color}-border'>
      <div class='player-title {color}'>{esc(nome)}</div>
      <div class='player-grid'>
        <div>
          <div class='rowline'><span>Sequência atual</span><span class='value-strong {seq_cor}'>{esc(resumo['sequencia'])}</span></div>
          <div class='rowline'><span>Partidas no último dia</span><span class='value-strong'>{situacao['jogos_ultimo_dia']}</span></div>
          <div class='rowline'><span>Vitórias no último dia</span><span class='value-strong green'>{situacao['vitorias_ultimo_dia']}</span></div>
          <div class='rowline'><span>Derrotas no último dia</span><span class='value-strong red'>{situacao['derrotas_ultimo_dia']}</span></div>
        </div>
        <div>
          <div class='rowline'><span>Aproveitamento geral</span><span class='value-strong {color}'>{resumo['aproveitamento']:.1f}%</span></div>
          <div class='rowline'><span>Desde a última partida</span><span class='value-strong'>{esc(formatar_tempo(situacao['tempo_sem_registro']))}</span></div>
          <div class='rowline'><span>Maior série de vitórias</span><span class='value-strong green'>{resumo['maior_v']}</span></div>
          <div class='rowline'><span>Maior série de derrotas</span><span class='value-strong red'>{resumo['maior_d']}</span></div>
        </div>
      </div>
    </div>"""


def styled_history_player(d: pd.DataFrame) -> pd.io.formats.style.Styler:
    t=tabela_historico(d)
    def color_result(v):
        return 'background-color:#153b22;color:#6dff8f;font-weight:800' if v=='Vitória' else 'background-color:#431a22;color:#ff7180;font-weight:800'
    return t.style.map(color_result, subset=['Resultado']).set_properties(**{'background-color':'#0b192b','color':'#f5f7fa','border-color':'#233850'}).set_table_styles([
        {'selector':'th','props':[('background-color','#102238'),('color','#ffffff'),('font-weight','800')]}
    ])


try:
    df = carregar_dados(); reg = criar_registros(df)
except Exception as exc:
    st.error(f"Não foi possível carregar o banco de dados: {exc}"); st.stop()

jogadores=sorted(reg['jogador'].dropna().unique().tolist())
ultima_atualizacao=df['data_hora'].max(); primeira_data=df['data_hora'].min()

st.sidebar.markdown("<div class='sidebar-kicker'>Sistema de análise</div><div class='sidebar-brand'>🏓 Inteligência do Tênis de Mesa</div>",unsafe_allow_html=True)
pagina=st.sidebar.radio('Navegação',['⚔️ Analisar confronto','👤 Perfil do jogador','📈 Padrões do campeonato','🗄️ Banco de dados','🧠 Inteligência'],label_visibility='collapsed')
st.sidebar.markdown(f"""<div class='db-card'><b>🗄️ Banco de dados</b><div style='margin-top:12px'>Partidas registradas</div><div class='db-num'>{len(df)}</div><div>Jogadores</div><div class='db-num'>{len(jogadores)}</div><div>Atualizado em</div><div class='db-time'>{ultima_atualizacao:%d/%m/%Y %H:%M}</div></div>""",unsafe_allow_html=True)

st.markdown("<div class='hero'><div><div class='hero-title'>🏓 Inteligência do Tênis de Mesa</div><div class='hero-sub'>Versão 2.0 • interface profissional, comparação e padrões progressivos.</div></div></div>",unsafe_allow_html=True)
st.markdown(f"<div class='statusbar'>ⓘ Último dado registrado: <b>{ultima_atualizacao:%d/%m/%Y às %H:%M}</b> &nbsp;•&nbsp; O banco pode ter atraso de até 24 horas.</div>",unsafe_allow_html=True)

if pagina=='⚔️ Analisar confronto':
    st.markdown("<div class='section-kicker'>Análise entre dois jogadores</div><div class='section-sub'>Histórico direto, momento atual e leitura visual de vitórias e derrotas.</div>",unsafe_allow_html=True)
    c1,cv,c2=st.columns([1,0.12,1])
    jogador_a=c1.selectbox('Jogador 1',jogadores,index=0)
    opcoes_b=[j for j in jogadores if j!=jogador_a]
    with cv: st.markdown("<div class='vs'>X</div>",unsafe_allow_html=True)
    jogador_b=c2.selectbox('Jogador 2',opcoes_b,index=0)
    da=dados_jogador(reg,jogador_a); db=dados_jogador(reg,jogador_b)
    ra=resumo_jogador(reg,jogador_a); rb=resumo_jogador(reg,jogador_b)
    sa=ultima_situacao_jogador(da,ultima_atualizacao); sb=ultima_situacao_jogador(db,ultima_atualizacao)
    confrontos=df[(((df['jogador_1']==jogador_a)&(df['jogador_2']==jogador_b))|((df['jogador_1']==jogador_b)&(df['jogador_2']==jogador_a)))].copy().sort_values(['data_hora','id'])
    rc=resumo_confronto(confrontos,jogador_a,jogador_b)
    cards=''.join([
      metric_card('Confrontos',rc['total'],'Total de partidas'),
      metric_card(f'Vitórias — {jogador_a}',rc['vit_a'],f"{rc['pct_a']:.1f}%",'green'),
      metric_card(f'Vitórias — {jogador_b}',rc['vit_b'],f"{rc['pct_b']:.1f}%",'red'),
      metric_card('Empates',0,'0%','yellow'),
      metric_card('Decididas no 5º set',rc['jogos_5_sets'],f"{rc['pct_5_sets']:.1f}%",'purple')])
    st.markdown(f"<div class='metric-grid'>{cards}</div>",unsafe_allow_html=True)
    a,b=st.columns(2)
    a.markdown(player_panel(jogador_a,ra,sa,'green'),unsafe_allow_html=True)
    b.markdown(player_panel(jogador_b,rb,sb,'red'),unsafe_allow_html=True)

    r1,r2,r3=st.columns(3)
    r1.markdown(f"<div class='results-card'><div class='results-title'>Últimos 10 resultados — {esc(jogador_a)}</div>{result_badges(da.tail(10)['resultado'].tolist())}</div>",unsafe_allow_html=True)
    r2.markdown(f"<div class='results-card'><div class='results-title'>Últimos 10 resultados — {esc(jogador_b)}</div>{result_badges(db.tail(10)['resultado'].tolist())}</div>",unsafe_allow_html=True)
    direct_a=[] if confrontos.empty else ['V' if x==jogador_a else 'D' for x in confrontos.tail(10)['vencedor']]
    r3.markdown(f"<div class='results-card'><div class='results-title'>Últimos 10 confrontos entre os dois</div>{result_badges(direct_a)}</div>",unsafe_allow_html=True)

    st.markdown("<div class='section-kicker'>Histórico de confrontos</div>",unsafe_allow_html=True)
    if confrontos.empty: st.info('Ainda não há confronto direto registrado.')
    else:
      h=confrontos.sort_values(['data_hora','id'],ascending=False).copy()
      h['Data']=h['data_hora'].dt.strftime('%d/%m/%Y %H:%M');h['Placar']=h['sets_j1'].astype(str)+' x '+h['sets_j2'].astype(str);h['Sets']=h['sets_j1']+h['sets_j2'];h['Resultado']='Vitória'
      show=h[['Data','vencedor','Placar','Sets','Resultado']].rename(columns={'vencedor':'Vencedor'})
      def winner_color(v): return 'color:#35d05b;font-weight:800' if v==jogador_a else 'color:#ff3b4e;font-weight:800'
      sty=show.style.map(winner_color,subset=['Vencedor']).map(lambda v:'background-color:#153b22;color:#6dff8f;font-weight:800',subset=['Resultado']).set_properties(**{'background-color':'#0b192b','color':'#f5f7fa','border-color':'#233850'}).set_table_styles([{'selector':'th','props':[('background-color','#102238'),('color','#fff'),('font-weight','800')]}])
      st.dataframe(sty,use_container_width=True,hide_index=True)
    st.markdown("<div class='section-kicker'>Padrões encontrados</div>",unsafe_allow_html=True)
    for tipo,texto in insights_confronto(confrontos,jogador_a,jogador_b): st.markdown(f"<div class='insight {'ok' if tipo=='ok' else 'warn'}'>{esc(texto)}</div>",unsafe_allow_html=True)

elif pagina=='👤 Perfil do jogador':
    st.markdown("<div class='section-kicker'>Perfil do jogador</div><div class='section-sub'>Volume, frequência, sequência e histórico com leitura rápida.</div>",unsafe_allow_html=True)
    jogador=st.selectbox('Selecione o jogador',jogadores)
    d=dados_jogador(reg,jogador);r=resumo_jogador(reg,jogador);s=ultima_situacao_jogador(d,ultima_atualizacao);p=padrao_intervalos(d)
    cards=''.join([metric_card('Partidas',r['jogos']),metric_card('Vitórias',r['vitorias'],color='green'),metric_card('Derrotas',r['derrotas'],color='red'),metric_card('Aproveitamento',f"{r['aproveitamento']:.1f}%",color='blue'),metric_card('Dias ativos',p['dias_ativos'],color='purple')])
    st.markdown(f"<div class='metric-grid'>{cards}</div>",unsafe_allow_html=True)
    st.markdown(player_panel(jogador,r,s,'green'),unsafe_allow_html=True)
    st.markdown(f"<div class='results-card'><div class='results-title'>Últimos 10 resultados</div>{result_badges(d.tail(10)['resultado'].tolist())}</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Padrões encontrados</div>",unsafe_allow_html=True)
    for tipo,texto in gerar_insights_jogador(d): st.markdown(f"<div class='insight {'ok' if tipo=='ok' else 'warn'}'>{esc(texto)}</div>",unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Histórico</div>",unsafe_allow_html=True)
    st.dataframe(styled_history_player(d),use_container_width=True,hide_index=True)

elif pagina=='📈 Padrões do campeonato':
    st.markdown("<div class='section-kicker'>Padrões do campeonato</div><div class='section-sub'>Volume geral, jogadores mais ativos e distribuição por horário.</div>",unsafe_allow_html=True)
    dias=df['data'].nunique();cards=''.join([metric_card('Partidas registradas',len(df)),metric_card('Jogadores',len(jogadores),color='blue'),metric_card('Dias no banco',dias,color='purple'),metric_card('Média de jogos/dia',f"{len(df)/dias:.1f}" if dias else '—',color='yellow'),metric_card('Período',f"{primeira_data:%d/%m}–{ultima_atualizacao:%d/%m}")])
    st.markdown(f"<div class='metric-grid'>{cards}</div>",unsafe_allow_html=True)
    volume=reg.groupby('jogador').agg(Partidas=('id','size'),Dias_ativos=('data','nunique'),Vitórias=('resultado',lambda s:int((s=='V').sum())))
    volume['Média por dia ativo']=volume['Partidas']/volume['Dias_ativos'];volume['Aproveitamento']=volume['Vitórias']/volume['Partidas']*100
    st.dataframe(volume.sort_values(['Média por dia ativo','Partidas'],ascending=False).head(25).round(1),use_container_width=True)
    horario=df['hora_num'].map(faixa_horaria).value_counts().reindex(['Madrugada','Manhã','Tarde','Noite'],fill_value=0)
    st.bar_chart(horario)

elif pagina=='🗄️ Banco de dados':
    st.markdown("<div class='section-kicker'>Banco de dados</div><div class='section-sub'>Consulta dos registros brutos utilizados nas análises.</div>",unsafe_allow_html=True)
    st.dataframe(df.sort_values('data_hora',ascending=False),use_container_width=True,hide_index=True)

else:
    st.markdown("<div class='section-kicker'>Central de inteligência</div><div class='section-sub'>Resumo automático dos sinais mais relevantes encontrados no banco atual.</div>",unsafe_allow_html=True)
    volume=reg.groupby('jogador').size().sort_values(ascending=False)
    if not volume.empty: st.markdown(f"<div class='insight ok'>Jogador com maior volume registrado: <b>{esc(volume.index[0])}</b>, com <b>{int(volume.iloc[0])}</b> partidas.</div>",unsafe_allow_html=True)
    aproveit=reg.groupby('jogador')['resultado'].apply(lambda s:(s=='V').mean()*100).sort_values(ascending=False)
    if not aproveit.empty: st.markdown(f"<div class='insight ok'>Maior aproveitamento atual: <b>{esc(aproveit.index[0])}</b>, com <b>{aproveit.iloc[0]:.1f}%</b>.</div>",unsafe_allow_html=True)
    st.markdown("<div class='insight warn'>As previsões de frequência ganharão confiança conforme o banco acumular mais datas diferentes.</div>",unsafe_allow_html=True)
