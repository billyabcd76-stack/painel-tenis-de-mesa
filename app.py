from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Inteligência do Tênis de Mesa",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {background: #07111f; color: #eef4ff;}
    [data-testid="stSidebar"] {background: #0b1727; border-right: 1px solid #1d3047;}
    div[data-testid="stMetric"] {
        background: #0e1b2d;
        border: 1px solid #26384e;
        padding: 14px;
        border-radius: 14px;
    }
    .status-box {
        padding: 12px 14px;
        border: 1px solid #26384e;
        border-radius: 12px;
        background: #0e1b2d;
        margin: 6px 0;
    }
    .insight {
        padding: 13px 15px;
        border-left: 4px solid #55c2ff;
        border-radius: 8px;
        background: #0e1b2d;
        margin: 8px 0;
    }
    .warning-insight {border-left-color: #f5b642;}
    .ok-insight {border-left-color: #48c78e;}
    .muted {color: #a9b8ca; font-size: .92rem;}
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
st.caption("Histórico, sequência, volume de partidas e descoberta progressiva de padrões.")

with st.container():
    st.markdown(
        f"<div class='status-box'><b>Último dado registrado:</b> {ultima_atualizacao:%d/%m/%Y às %H:%M} "
        f"<span class='muted'>• O banco pode ter atraso de até 24 horas.</span></div>",
        unsafe_allow_html=True,
    )

if pagina == "⚔️ Analisar confronto":
    st.subheader("Análise entre dois jogadores")
    c1, c2 = st.columns(2)
    jogador_a = c1.selectbox("Jogador A", jogadores, index=0)
    opcoes_b = [j for j in jogadores if j != jogador_a]
    jogador_b = c2.selectbox("Jogador B", opcoes_b, index=0)

    da = dados_jogador(reg, jogador_a)
    db = dados_jogador(reg, jogador_b)
    ra = resumo_jogador(reg, jogador_a)
    rb = resumo_jogador(reg, jogador_b)

    confrontos = df[
        ((df["jogador_1"] == jogador_a) & (df["jogador_2"] == jogador_b))
        | ((df["jogador_1"] == jogador_b) & (df["jogador_2"] == jogador_a))
    ].copy().sort_values(["data_hora", "id"])

    vit_a = int((confrontos["vencedor"] == jogador_a).sum())
    vit_b = int((confrontos["vencedor"] == jogador_b).sum())

    m1, m2, m3 = st.columns(3)
    m1.metric("Confrontos diretos", len(confrontos))
    m2.metric(f"Vitórias — {jogador_a}", vit_a)
    m3.metric(f"Vitórias — {jogador_b}", vit_b)

    st.markdown("### Situação registrada")
    a, b = st.columns(2)
    for col, nome, r, dados in [(a, jogador_a, ra, da), (b, jogador_b, rb, db)]:
        with col:
            st.markdown(f"#### {nome}")
            x1, x2 = st.columns(2)
            x1.metric("Sequência atual", r["sequencia"])
            x2.metric("Aproveitamento", f"{r['aproveitamento']:.1f}%")
            ultima_data = dados["data"].max()
            jogos_ultimo_dia = int((dados["data"] == ultima_data).sum())
            st.write(f"**Partidas no último dia registrado:** {jogos_ultimo_dia}")
            st.write(f"**Última partida registrada:** {r['ultima']:%d/%m/%Y %H:%M}")
            st.write(f"**Distância até o fechamento do banco:** {formatar_tempo(ultima_atualizacao - r['ultima'])}")

    if confrontos.empty:
        st.info("Ainda não há confronto direto entre esses jogadores no banco atual.")
    else:
        resultados_h2h_a = []
        for _, r in confrontos.iterrows():
            resultados_h2h_a.append("V" if r["vencedor"] == jogador_a else "D")
        _, _, seq_h2h, _ = sequencias(resultados_h2h_a)
        ultimo_vencedor = confrontos.iloc[-1]["vencedor"]

        st.markdown("### Padrões do confronto")
        i1, i2, i3 = st.columns(3)
        i1.metric("Líder do histórico", jogador_a if vit_a > vit_b else jogador_b if vit_b > vit_a else "Empate")
        i2.metric(f"Sequência de {jogador_a}", seq_h2h)
        i3.metric("Vencedor do último", ultimo_vencedor)

        por_dia = confrontos.groupby("data").size()
        st.write(
            f"**Volume do confronto:** média de {por_dia.mean():.1f} encontro(s) por dia em que se enfrentaram; "
            f"máximo de {int(por_dia.max())}."
        )

        h = confrontos.sort_values(["data_hora", "id"], ascending=False).copy()
        h["Data"] = h["data_hora"].dt.strftime("%d/%m/%Y")
        h["Hora"] = h["data_hora"].dt.strftime("%H:%M")
        h["Placar"] = h["sets_j1"].astype(str) + " x " + h["sets_j2"].astype(str)
        st.dataframe(
            h[["Data", "Hora", "jogador_1", "jogador_2", "Placar", "vencedor"]].rename(
                columns={"jogador_1": "Jogador 1", "jogador_2": "Jogador 2", "vencedor": "Vencedor"}
            ),
            use_container_width=True,
            hide_index=True,
        )

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
