from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Inteligência do Tênis de Mesa — V1.2.1",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --fundo: #07111f;
        --painel: #0e1b2d;
        --painel-2: #102238;
        --borda: #35506f;
        --texto: #ffffff;
        --texto-secundario: #d7e2ef;
        --destaque: #ff4fa3;
    }

    .stApp {background: var(--fundo); color: var(--texto);}
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: var(--texto);
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #ffffff !important;
    }
    [data-testid="stHeader"] {background: rgba(7,17,31,.96);}
    [data-testid="stSidebar"] {
        background: #0b1727;
        border-right: 1px solid var(--borda);
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: #102238;
        border: 1px solid #294461;
        border-radius: 10px;
        padding: 10px 12px;
        margin-bottom: 7px;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: #17314e;
        border-color: #54789f;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #b51f64, #5b2b77);
        border-color: #ff69ad;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #e8f0fa !important;
        font-weight: 600;
    }

    div[data-testid="stMetric"] {
        background: var(--painel);
        border: 1px solid var(--borda);
        padding: 14px;
        border-radius: 14px;
        box-shadow: none;
    }
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] p {
        color: #dce8f5 !important;
        font-size: .95rem !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #dce8f5 !important;
        opacity: 1 !important;
    }
    [data-testid="stMetricDelta"] svg {fill: currentColor !important;}

    [data-baseweb="tab-list"] button {
        color: #dce8f5 !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }
    [data-baseweb="tab-list"] button[aria-selected="true"] {
        color: #ffffff !important;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    .stTextInput input {
        background: #f7fafc !important;
        color: #101820 !important;
        border-color: #8ea5bd !important;
    }
    [data-baseweb="select"] * {
        color: #101820 !important;
        opacity: 1 !important;
    }
    [data-baseweb="popover"] * {color: #101820 !important;}

    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: var(--painel);
        border-radius: 12px;
    }
    [data-testid="stDataFrame"] * {opacity: 1 !important;}
    .stCaptionContainer p, .stMarkdown small {
        color: var(--texto-secundario) !important;
        opacity: 1 !important;
    }
    .stMarkdown p, .stMarkdown li, .stMarkdown strong {
        color: #f4f8fc !important;
        opacity: 1 !important;
    }

    .status-box {
        padding: 12px 14px;
        border: 1px solid var(--borda);
        border-radius: 12px;
        background: var(--painel-2);
        margin: 6px 0;
        color: #ffffff !important;
        font-weight: 600;
    }
    .insight {
        padding: 13px 15px;
        border-left: 4px solid #55c2ff;
        border-radius: 8px;
        background: var(--painel);
        margin: 8px 0;
        color: #ffffff !important;
        font-weight: 600;
    }
    .warning-insight {border-left-color: #f5b642;}
    .ok-insight {border-left-color: #48c78e;}
    .muted {color: #d7e2ef !important; font-size: .92rem; opacity: 1 !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

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


try:
    df = carregar_dados()
    reg = criar_registros(df)
except Exception as exc:
    st.error(f"Não foi possível carregar o banco de dados: {exc}")
    st.stop()

jogadores = sorted(reg["jogador"].dropna().unique().tolist())
ultima_atualizacao = df["data_hora"].max()
primeira_data = df["data_hora"].min()

st.sidebar.markdown("## 🏓 Sistema de análise")
pagina = st.sidebar.radio(
    "Navegação",
    [
        "⚔️ Analisar confronto",
        "👤 Perfil do jogador",
        "🧠 Padrões do campeonato",
        "📋 Histórico geral",
    ],
)
st.sidebar.divider()
st.sidebar.caption(
    f"Banco: {len(df)} partidas • {len(jogadores)} jogadores\n\n"
    f"Atualizado até {ultima_atualizacao:%d/%m/%Y %H:%M}"
)

st.title("🏓 Inteligência do Tênis de Mesa")
st.caption("Versão 1.2.1 • contraste corrigido para melhor leitura.")

with st.container():
    st.markdown(
        f"<div class='status-box'><b>Último dado registrado:</b> {ultima_atualizacao:%d/%m/%Y às %H:%M} "
        f"<span class='muted'>• O banco pode ter atraso de até 24 horas.</span></div>",
        unsafe_allow_html=True,
    )

if pagina == "⚔️ Analisar confronto":
    st.subheader("Confronto inteligente")
    st.caption("Compare o histórico direto e o momento registrado dos dois jogadores.")

    c1, c2 = st.columns(2)
    jogador_a = c1.selectbox("Jogador A", jogadores, index=0)
    opcoes_b = [j for j in jogadores if j != jogador_a]
    jogador_b = c2.selectbox("Jogador B", opcoes_b, index=0)

    da = dados_jogador(reg, jogador_a)
    db = dados_jogador(reg, jogador_b)
    ra = resumo_jogador(reg, jogador_a)
    rb = resumo_jogador(reg, jogador_b)
    sa = ultima_situacao_jogador(da, ultima_atualizacao)
    sb = ultima_situacao_jogador(db, ultima_atualizacao)

    confrontos = df[
        ((df["jogador_1"] == jogador_a) & (df["jogador_2"] == jogador_b))
        | ((df["jogador_1"] == jogador_b) & (df["jogador_2"] == jogador_a))
    ].copy().sort_values(["data_hora", "id"])
    rc = resumo_confronto(confrontos, jogador_a, jogador_b)

    st.markdown(f"### {jogador_a}  ×  {jogador_b}")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Confrontos diretos", rc["total"])
    m2.metric(f"Vitórias — {jogador_a}", rc["vit_a"], f"{rc['pct_a']:.1f}% do confronto")
    m3.metric(f"Vitórias — {jogador_b}", rc["vit_b"], f"{rc['pct_b']:.1f}% do confronto")
    m4.metric("Classificação", rc["classificacao"])

    if rc["total"]:
        st.progress(rc["pct_a"] / 100, text=f"Participação histórica de vitórias: {jogador_a} {rc['pct_a']:.1f}% × {rc['pct_b']:.1f}% {jogador_b}")
        st.caption("Este percentual descreve o histórico registrado; não é uma probabilidade garantida para a próxima partida.")

    tab_resumo, tab_linha, tab_padroes = st.tabs(["📊 Resumo", "🕒 Linha do tempo", "🧠 Padrões"])

    with tab_resumo:
        st.markdown("### Momento dos jogadores")
        a, b = st.columns(2)
        for col, nome, r, situacao in [(a, jogador_a, ra, sa), (b, jogador_b, rb, sb)]:
            with col:
                st.markdown(f"#### {nome}")
                x1, x2 = st.columns(2)
                x1.metric("Sequência atual", r["sequencia"])
                x2.metric("Aproveitamento geral", f"{r['aproveitamento']:.1f}%")
                y1, y2 = st.columns(2)
                y1.metric("Jogos no último dia", situacao["jogos_ultimo_dia"])
                y2.metric("Saldo no último dia", situacao["vitorias_ultimo_dia"] - situacao["derrotas_ultimo_dia"], f"{situacao['vitorias_ultimo_dia']}V • {situacao['derrotas_ultimo_dia']}D")
                st.write(f"**Última partida registrada:** {situacao['ultima']:%d/%m/%Y %H:%M}")
                st.write(f"**Tempo desde o último registro:** {formatar_tempo(situacao['tempo_sem_registro'])}")
                st.caption(f"Confiança do tempo sem jogar: {situacao['confianca']}")

        st.markdown("### Comparativo rápido")
        comparativo = pd.DataFrame({
            "Indicador": [
                "Partidas no banco", "Vitórias", "Derrotas", "Aproveitamento",
                "Sequência atual", "Maior sequência de vitórias",
                "Maior sequência de derrotas", "Partidas no último dia registrado"
            ],
            jogador_a: [ra["jogos"], ra["vitorias"], ra["derrotas"], f"{ra['aproveitamento']:.1f}%", ra["sequencia"], ra["maior_v"], ra["maior_d"], sa["jogos_ultimo_dia"]],
            jogador_b: [rb["jogos"], rb["vitorias"], rb["derrotas"], f"{rb['aproveitamento']:.1f}%", rb["sequencia"], rb["maior_v"], rb["maior_d"], sb["jogos_ultimo_dia"]],
        })
        st.dataframe(comparativo, use_container_width=True, hide_index=True)

        st.markdown("### Últimos resultados")
        u1, u2 = st.columns(2)
        u1.markdown(f"**{jogador_a} — geral:** {' '.join(da.tail(10)['resultado'].tolist()) or '—'}")
        u1.markdown(f"**{jogador_a} — neste confronto:** {ultimos_resultados_confronto(confrontos, jogador_a)}")
        u2.markdown(f"**{jogador_b} — geral:** {' '.join(db.tail(10)['resultado'].tolist()) or '—'}")
        u2.markdown(f"**{jogador_b} — neste confronto:** {ultimos_resultados_confronto(confrontos, jogador_b)}")

    with tab_linha:
        if confrontos.empty:
            st.info("Ainda não há confronto direto entre esses jogadores no banco atual.")
        else:
            h = confrontos.sort_values(["data_hora", "id"], ascending=False).copy()
            h["Data"] = h["data_hora"].dt.strftime("%d/%m/%Y")
            h["Hora"] = h["data_hora"].dt.strftime("%H:%M")
            h["Confronto"] = h["jogador_1"] + " " + h["sets_j1"].astype(str) + " × " + h["sets_j2"].astype(str) + " " + h["jogador_2"]
            h["Total de sets"] = h["sets_j1"] + h["sets_j2"]
            st.dataframe(
                h[["Data", "Hora", "Confronto", "vencedor", "Total de sets"]].rename(columns={"vencedor": "Vencedor"}),
                use_container_width=True, hide_index=True,
            )
            st.markdown("### Resumo por dia")
            dias = confrontos.groupby("data").agg(
                Confrontos=("id", "size"),
                Vitorias_A=("vencedor", lambda s: int((s == jogador_a).sum())),
                Vitorias_B=("vencedor", lambda s: int((s == jogador_b).sum())),
            ).reset_index()
            dias["Data"] = pd.to_datetime(dias["data"]).dt.strftime("%d/%m/%Y")
            dias = dias.rename(columns={"Vitorias_A": f"Vitórias — {jogador_a}", "Vitorias_B": f"Vitórias — {jogador_b}"})
            st.dataframe(dias.drop(columns="data"), use_container_width=True, hide_index=True)

    with tab_padroes:
        p1, p2, p3 = st.columns(3)
        p1.metric("Partidas decididas no 5º set", rc["jogos_5_sets"], f"{rc['pct_5_sets']:.1f}%")
        p2.metric(f"Últimos 10 — {jogador_a}", ultimos_resultados_confronto(confrontos, jogador_a))
        p3.metric(f"Últimos 10 — {jogador_b}", ultimos_resultados_confronto(confrontos, jogador_b))
        for tipo, texto in insights_confronto(confrontos, jogador_a, jogador_b):
            classe = "ok-insight" if tipo == "ok" else "warning-insight"
            st.markdown(f"<div class='insight {classe}'>{texto}</div>", unsafe_allow_html=True)

        st.markdown("### Padrões individuais relevantes")
        ia, ib = st.columns(2)
        for col, nome, dados in [(ia, jogador_a, da), (ib, jogador_b, db)]:
            with col:
                st.markdown(f"#### {nome}")
                encontrados = gerar_insights_jogador(dados)
                if encontrados:
                    for tipo, texto in encontrados:
                        classe = "ok-insight" if tipo == "ok" else "warning-insight"
                        st.markdown(f"<div class='insight {classe}'>{texto}</div>", unsafe_allow_html=True)
                else:
                    st.info("Ainda não há dados suficientes para encontrar padrões.")

elif pagina == "👤 Perfil do jogador":
    st.subheader("Perfil inteligente do jogador")
    termo = st.text_input("Pesquisar pelo nome", placeholder="Digite parte do nome")
    encontrados = [j for j in jogadores if termo.strip().lower() in j.lower()] if termo.strip() else jogadores
    if not encontrados:
        st.warning("Nenhum jogador encontrado.")
        st.stop()

    jogador = st.selectbox("Selecione o jogador", encontrados)
    d = dados_jogador(reg, jogador)
    r = resumo_jogador(reg, jogador)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Partidas", r["jogos"])
    c2.metric("Vitórias", r["vitorias"])
    c3.metric("Derrotas", r["derrotas"])
    c4.metric("Aproveitamento", f"{r['aproveitamento']:.1f}%")

    st.markdown("### Momento e volume")
    a, b = st.columns(2)
    with a:
        st.write(f"**Sequência atual:** {r['sequencia']}")
        st.write(f"**Maior sequência de vitórias:** {r['maior_v']}")
        st.write(f"**Maior sequência de derrotas:** {r['maior_d']}")
        ultimos = " ".join(d.tail(10)["resultado"].tolist())
        st.write(f"**Últimos 10:** {ultimos}")

    with b:
        por_dia = d.groupby("data").size().sort_index()
        st.write(f"**Dias ativos registrados:** {len(por_dia)}")
        st.write(f"**Média por dia ativo:** {por_dia.mean():.1f}")
        st.write(f"**Máximo em um dia:** {int(por_dia.max())}")
        st.write(f"**Última partida registrada:** {r['ultima']:%d/%m/%Y %H:%M}")

    st.markdown("### Frequência de aparição")
    p = padrao_intervalos(d)
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Dias ativos", p["dias_ativos"])
    f2.metric("Intervalo médio", f"{p['media']:.1f} dias" if p["media"] is not None else "Aguardando dados")
    f3.metric("Intervalo mais comum", f"{p['moda']} dias" if p["moda"] is not None else "Aguardando dados")
    f4.metric("Regularidade", f"{p['regularidade']:.0f}%" if p["regularidade"] is not None else "Aguardando dados")

    if p["dias_ativos"] < 4:
        st.warning("O banco ainda não possui dias suficientes para definir o ciclo de aparição deste jogador. A análise será ativada automaticamente conforme novas datas forem adicionadas.")

    st.markdown("### Desempenho conforme a partida do dia")
    ordem = d.groupby("ordem_no_dia").agg(
        Partidas=("resultado", "size"),
        Vitórias=("resultado", lambda s: int((s == "V").sum())),
    )
    ordem["Aproveitamento"] = ordem["Vitórias"] / ordem["Partidas"] * 100
    ordem.index.name = "Partida do dia"
    st.dataframe(ordem.round({"Aproveitamento": 1}), use_container_width=True)

    st.markdown("### Padrões encontrados")
    for tipo, texto in gerar_insights_jogador(d):
        classe = "ok-insight" if tipo == "ok" else "warning-insight"
        st.markdown(f"<div class='insight {classe}'>{texto}</div>", unsafe_allow_html=True)

    st.markdown("### Histórico")
    st.dataframe(tabela_historico(d), use_container_width=True, hide_index=True)

elif pagina == "🧠 Padrões do campeonato":
    st.subheader("Padrões gerais do campeonato")
    dias_banco = df["data"].nunique()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Partidas registradas", len(df))
    c2.metric("Jogadores", len(jogadores))
    c3.metric("Dias no banco", dias_banco)
    c4.metric("Média de jogos/dia", f"{len(df) / dias_banco:.1f}" if dias_banco else "—")

    st.markdown("### Jogadores com maior volume")
    volume = reg.groupby("jogador").agg(
        Partidas=("id", "size"),
        Dias_ativos=("data", "nunique"),
        Vitórias=("resultado", lambda s: int((s == "V").sum())),
    )
    volume["Média por dia ativo"] = volume["Partidas"] / volume["Dias_ativos"]
    volume["Aproveitamento"] = volume["Vitórias"] / volume["Partidas"] * 100
    volume = volume.sort_values(["Média por dia ativo", "Partidas"], ascending=False)
    st.dataframe(volume.head(25).round(1), use_container_width=True)

    st.markdown("### Distribuição por horário")
    horario = df["hora_num"].map(faixa_horaria).value_counts().reindex(["Madrugada", "Manhã", "Tarde", "Noite"], fill_value=0)
    st.bar_chart(horario)

    st.markdown("### Estado da descoberta de padrões")
    if dias_banco < 4:
        st.warning(
            "O banco atual cobre apenas uma pequena quantidade de dias. Já é possível analisar confrontos, sequências e volume dentro do dia, mas os padrões de escala, rodízio e retorno precisarão de pelo menos 4 dias distintos para começar a aparecer."
        )
    else:
        st.success("Já existem datas suficientes para iniciar a análise de frequência e rodízio.")

    st.markdown("### Pares que mais se enfrentaram")
    pares = df.apply(lambda r: " × ".join(sorted([r["jogador_1"], r["jogador_2"]])), axis=1).value_counts().head(20)
    st.dataframe(pares.rename("Confrontos").to_frame(), use_container_width=True)

else:
    st.subheader("Histórico geral")
    geral = df.sort_values(["data_hora", "id"], ascending=False).copy()
    geral["Data"] = geral["data_hora"].dt.strftime("%d/%m/%Y")
    geral["Hora"] = geral["data_hora"].dt.strftime("%H:%M")
    geral["Placar"] = geral["sets_j1"].astype(str) + " x " + geral["sets_j2"].astype(str)
    st.dataframe(
        geral[["id", "Data", "Hora", "jogador_1", "jogador_2", "Placar", "vencedor"]].rename(
            columns={"id": "ID", "jogador_1": "Jogador 1", "jogador_2": "Jogador 2", "vencedor": "Vencedor"}
        ),
        use_container_width=True,
        hide_index=True,
    )

st.divider()
st.caption(
    f"Período atualmente registrado: {primeira_data:%d/%m/%Y %H:%M} a {ultima_atualizacao:%d/%m/%Y %H:%M}. "
    "As previsões de frequência só serão exibidas quando houver histórico suficiente em datas diferentes."
)
