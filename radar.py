import plotly.graph_objects as go
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def generate_radar(target_name, candidate_name, target_raw, candidate_raw, population_raw, columns):
    scaler = MinMaxScaler()
    scaler.fit(population_raw)
    
    target_scaled = scaler.transform(target_raw)[0]
    candidate_scaled = scaler.transform(candidate_raw)[0]
    
    target_scaled = np.append(target_scaled, target_scaled[0])
    candidate_scaled = np.append(candidate_scaled, candidate_scaled[0])

    target_raw_values = np.append(target_raw.values[0], target_raw.values[0][0])
    candidate_raw_values = np.append(candidate_raw.values[0], candidate_raw.values[0][0])

    close_cols = columns + [columns[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=target_scaled,
        theta=close_cols,
        fill='toself',
        name=str(target_name),
        line_color='#1a85ff',
        mode='lines+markers',
        hoveron='points', 
        customdata=target_raw_values,
        hovertemplate="<b>%{theta}</b><br>" + str(target_name) + ": %{customdata:.2f}<extra></extra>"
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=candidate_scaled,
        theta=close_cols,
        fill='toself',
        name=str(candidate_name),
        line_color='#d41159',
        mode='lines+markers',
        hoveron='points', 
        customdata=candidate_raw_values,
        hovertemplate="<b>%{theta}</b><br>" + str(candidate_name) + ": %{customdata:.2f}<extra></extra>"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1])
        ),
        showlegend=True,
        title=dict(text=f"Tactic Comparison: {target_name} vs {candidate_name}", font=dict(size=18))
    )

    # name_file = f"radar_{candidate_name.replace(' ', '_')}.html"
    # fig.write_html(name_file, auto_open=True)

    return fig
