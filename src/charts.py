from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import RATING_LABELS
from src.metrics import (
    RATING_VALUES,
    annotation_frequencies,
    annotation_rating_distribution,
    dialogue_lengths,
    real_user_turns,
)


COLOR_SEQUENCE = ["#2563eb", "#059669", "#d97706", "#dc2626", "#7c3aed", "#0891b2"]


def rating_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras com a distribuição de satisfação."""
    data = real_user_turns(df).dropna(subset=["satisfaction_mode"])
    counts = (
        data.groupby(["dataset", "satisfaction_mode"], as_index=False)
        .size()
        .rename(columns={"size": "total"})
    )

    fig = px.bar(
        counts,
        x="satisfaction_mode",
        y="total",
        color="dataset",
        barmode="group",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={
            "satisfaction_mode": "Satisfação",
            "total": "Total de turnos",
            "dataset": "Dataset",
        },
    )
    fig.update_layout(legend_title_text="Dataset")
    return fig


def dialogues_by_dataset_chart(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico com a quantidade de diálogos por dataset."""
    counts = (
        df.groupby("dataset", as_index=False)["dialogue_id"]
        .nunique()
        .rename(columns={"dialogue_id": "dialogues"})
    )

    return px.bar(
        counts,
        x="dataset",
        y="dialogues",
        color="dataset",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={"dataset": "Dataset", "dialogues": "Diálogos"},
    )


def top_actions_chart(df: pd.DataFrame, limit: int = 15) -> go.Figure:
    """Cria gráfico com as ações mais frequentes no recorte selecionado."""
    data = real_user_turns(df)
    counts = data["action_raw"].value_counts().head(limit).reset_index()
    counts.columns = ["action_raw", "total"]

    return px.bar(
        counts,
        x="total",
        y="action_raw",
        orientation="h",
        color="total",
        color_continuous_scale="Viridis",
        labels={"total": "Total", "action_raw": "Ação"},
    )


def disagreement_chart(df: pd.DataFrame) -> go.Figure:
    """Cria histograma da divergência entre anotadores."""
    data = real_user_turns(df).dropna(subset=["satisfaction_disagreement"])

    return px.histogram(
        data,
        x="satisfaction_disagreement",
        nbins=20,
        color="dataset",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={
            "satisfaction_disagreement": "Divergência",
            "count": "Total",
            "dataset": "Dataset",
        },
    )


def dialogue_length_chart(df: pd.DataFrame) -> go.Figure:
    """Cria boxplot com o tamanho dos diálogos por dataset."""
    lengths = dialogue_lengths(df)

    return px.box(
        lengths,
        x="dataset",
        y="turn_count",
        color="dataset",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={"dataset": "Dataset", "turn_count": "Turnos por diálogo"},
    )


def satisfaction_timeline_chart(dialogue_df: pd.DataFrame) -> go.Figure:
    """Cria linha temporal da satisfação dentro de um diálogo."""
    user_rows = dialogue_df[
        (dialogue_df["role"] == "USER") & (~dialogue_df["is_overall"])
    ].dropna(subset=["satisfaction_mode"])

    fig = px.line(
        user_rows,
        x="turn_id",
        y="satisfaction_mode",
        markers=True,
        labels={"turn_id": "Turno", "satisfaction_mode": "Satisfação"},
    )
    fig.update_yaxes(range=[0.8, 5.2], dtick=1)
    return fig


def action_rating_heatmap(df: pd.DataFrame, action_limit: int = 12) -> go.Figure:
    """Cria heatmap entre ações frequentes e notas de satisfação."""
    data = real_user_turns(df).dropna(subset=["satisfaction_mode"])
    top_actions = data["action_raw"].value_counts().head(action_limit).index
    data = data[data["action_raw"].isin(top_actions)]

    pivot = pd.crosstab(data["action_raw"], data["satisfaction_mode"])
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="Blues",
        labels={"x": "Satisfação", "y": "Ação", "color": "Total"},
    )
    return fig


def annotation_frequency_chart(
    df: pd.DataFrame,
    dataset_name: str,
    limit: int = 15,
    include_unknown: bool = True,
) -> go.Figure:
    """Cria barras horizontais com as anotações mais frequentes do dataset."""
    counts = annotation_frequencies(
        df,
        limit=limit,
        include_unknown=include_unknown,
    )

    fig = px.bar(
        counts,
        x="total",
        y="action_raw",
        orientation="h",
        color_discrete_sequence=["#0f766e"],
        labels={
            "total": "Quantidade de falas",
            "action_raw": "Anotação",
        },
        title=f"Quais anotações aparecem mais em {dataset_name}?",
        custom_data=["percentual"],
    )
    fig.update_traces(
        hovertemplate=(
            "Anotação: %{y}<br>"
            "Falas: %{x}<br>"
            "Percentual: %{customdata[0]:.1f}%<extra></extra>"
        )
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(showlegend=False)
    return fig


def annotation_rating_heatmap(
    df: pd.DataFrame,
    dataset_name: str,
    limit: int = 15,
    include_unknown: bool = True,
) -> go.Figure:
    """Cria mapa de calor entre anotações e notas de satisfação."""
    frequent_annotations = annotation_frequencies(
        df,
        limit=limit,
        include_unknown=include_unknown,
    )["action_raw"].tolist()
    counts, percentages = annotation_rating_distribution(
        df,
        annotations=frequent_annotations,
        include_unknown=include_unknown,
    )

    x_labels = [str(value) for value in RATING_VALUES]
    text = percentages.round(0).astype(int).astype(str) + "%"

    fig = go.Figure(
        data=go.Heatmap(
            z=percentages.to_numpy(),
            x=x_labels,
            y=percentages.index.tolist(),
            text=text.to_numpy(),
            texttemplate="%{text}",
            customdata=counts.to_numpy(),
            zmin=0,
            zmax=100,
            colorscale="Blues",
            colorbar={"title": "% das falas"},
            hovertemplate=(
                "Anotação: %{y}<br>"
                "Nota: %{x}<br>"
                "% das falas da anotação: %{z:.1f}%<br>"
                "Falas: %{customdata}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=f"Como as notas se distribuem dentro de cada anotação de {dataset_name}?",
        xaxis_title="Nota mais frequente",
        yaxis_title="Anotação",
    )
    fig.update_xaxes(
        tickmode="array",
        tickvals=x_labels,
        ticktext=[f"{value} · {RATING_LABELS[value]}" for value in RATING_VALUES],
    )
    return fig


def low_satisfaction_chart(low_rate_df: pd.DataFrame) -> go.Figure:
    """Cria gráfico da proporção de baixa satisfação por dataset."""
    return px.bar(
        low_rate_df,
        x="dataset",
        y="low_satisfaction",
        color="dataset",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={
            "dataset": "Dataset",
            "low_satisfaction": "Baixa satisfação (%)",
        },
    )


def three_class_distribution_chart(counts_df: pd.DataFrame) -> go.Figure:
    """Cria gráfico com a distribuição das classes agregadas de satisfação."""
    return px.bar(
        counts_df,
        x="dataset",
        y="total",
        color="satisfaction_3_classes",
        barmode="group",
        color_discrete_sequence=COLOR_SEQUENCE,
        labels={
            "dataset": "Dataset",
            "total": "Total",
            "satisfaction_3_classes": "Classe",
        },
    )
