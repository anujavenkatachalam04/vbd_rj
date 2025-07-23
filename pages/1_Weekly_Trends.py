def plot_temperature(df):
    fig = go.Figure()
    fig.add_bar(x=df["week_start_date"], y=df["dengue_cases"], name="Dengue Cases", marker_color="crimson", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["temperature_2m_max"], name="Max Temp", mode="lines+markers", line=dict(color="orange"), yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["temperature_2m_mean"], name="Mean Temp", mode="lines+markers", line=dict(color="darkorange"), yaxis="y2"))
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["temperature_2m_min"], name="Min Temp", mode="lines+markers", line=dict(color="blue"), yaxis="y2"))

    for dt in df[df["temperature_2m_max"] <= max_temp_threshold]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + pd.Timedelta(days=6), fillcolor="orange", opacity=0.1, line_width=0)

    for dt in df[df["temperature_2m_min"] >= min_temp_threshold]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + pd.Timedelta(days=6), fillcolor="blue", opacity=0.1, line_width=0)

    try:
        fig.update_layout(
            title="Temperature and Dengue Cases",
            xaxis=dict(title="Week", tickangle=-45, tickfont=dict(size=11, color='black')),
            yaxis=dict(title="Dengue Cases", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            yaxis2=dict(title="Temperature (°C)", overlaying="y", side="right", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=12, color='black')),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    except Exception as e:
        st.error(f"Plot layout error: {e!s}")
        raise

    return fig


def plot_rainfall(df):
    fig = go.Figure()
    fig.add_bar(x=df["week_start_date"], y=df["dengue_cases"], name="Dengue Cases", marker_color="crimson", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["rain_sum"], name="Rainfall (mm)", mode="lines+markers", line=dict(color="purple"), yaxis="y2"))

    for dt in df[df["rain_sum"].between(min_rainfall, max_rainfall)]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + pd.Timedelta(days=6), fillcolor="purple", opacity=0.1, line_width=0)

    try:
        fig.update_layout(
            title="Rainfall and Dengue Cases",
            xaxis=dict(title="Week", tickangle=-45, tickfont=dict(size=11, color='black')),
            yaxis=dict(title="Dengue Cases", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            yaxis2=dict(title="Rainfall (mm)", overlaying="y", side="right", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=12, color='black')),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    except Exception as e:
        st.error(f"Plot layout error: {e!s}")
        raise

    return fig


def plot_humidity(df):
    fig = go.Figure()
    fig.add_bar(x=df["week_start_date"], y=df["dengue_cases"], name="Dengue Cases", marker_color="crimson", yaxis="y1")
    fig.add_trace(go.Scatter(x=df["week_start_date"], y=df["relative_humidity_2m_mean"], name="Humidity (%)", mode="lines+markers", line=dict(color="green"), yaxis="y2"))

    for dt in df[df["relative_humidity_2m_mean"].between(min_rh, max_rh)]["week_start_date"]:
        fig.add_vrect(x0=dt, x1=dt + pd.Timedelta(days=6), fillcolor="green", opacity=0.1, line_width=0)

    try:
        fig.update_layout(
            title="Humidity and Dengue Cases",
            xaxis=dict(title="Week", tickangle=-45, tickfont=dict(size=11, color='black')),
            yaxis=dict(title="Dengue Cases", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            yaxis2=dict(title="Humidity (%)", overlaying="y", side="right", titlefont=dict(size=12, color='black'), tickfont=dict(size=11, color='black')),
            legend=dict(orientation="h", y=-0.3, x=0.5, xanchor="center", font=dict(size=12, color='black')),
            height=500,
            plot_bgcolor="white",
            paper_bgcolor="white"
        )
    except Exception as e:
        st.error(f"Plot layout error: {e!s}")
        raise

    return fig
