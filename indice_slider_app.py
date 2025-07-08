import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def plot_fuzzy_membership(fuzzy_scale, x_range=(0, 10), title="Fuzzy Membership Functions", figsize=(9, 7)):
    """
    Plots triangular fuzzy membership functions.

    Parameters:
        fuzzy_scale (dict): Dictionary of fuzzy sets with (a, b, c) triangle parameters.
        x_range (tuple): Range of x values to plot (start, end).
        title (str): Title of the plot.
        figsize (tuple): Size of the figure (width, height).
    """
    def triangular(x, a, b, c):
        return np.where(x <= a, 0,
                        np.where(x <= b, (x - a) / (b - a),
                                 np.where(x <= c, (c - x) / (c - b), 0)))

    x = np.linspace(*x_range, 500)

    fig, ax = plt.subplots(figsize=figsize)

    for label, (a, b, c) in fuzzy_scale.items():
        y = triangular(x, a, b, c)
        ax.plot(x, y, label=f"Level {label}")
        ax.fill_between(x, y, alpha=0.1)

    ax.set_title(title)
    ax.set_xlabel("Input Value")
    ax.set_ylabel("Membership Degree")
    ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
    ax.grid(True)
    plt.tight_layout()

    return fig, ax


#st.set_page_config(page_title="AHP e FAHP", layout="centered")
#st.title("📊 AHP vs FAHP")
#st.markdown("Compare e avalie pesos de critérios com métodos clássico (AHP) e fuzzy (FAHP).")


st.set_page_config(page_title="Índice de vulnerabilidade hídrica natural em bacias hidrográficas", layout="centered")
st.title("📊 Índice de vulnerabilidade hídrica natural em bacias hidrográficas")
st.markdown(
'''
O presente estudo utiliza a metodologia **Fuzzy AHP** para desenvolver um **índice 
de vulnerabilidade hídrica natural em bacias hidrográficas**. 
A técnica permite hierarquizar e ponderar critérios com maior precisão, 
considerando incertezas inerentes ao processo decisório. 
Os **pesos obtidos** são aplicados em geoprocessamento, 
viabilizando análises espaciais mais robustas e apoiando a gestão ambiental integrada.
'''
)
st.markdown(
'''
Nesse contexto, foram elencados cinco fatores, a saber: 
**precipitação, elevação, declividade, uso e cobertura do solo e textura do solo**, 
que serão submetidos à especialistas para realização de comparações
 pareadas através de uma escala de importância.
'''
)

st.image('5_fatores.png')


# Critérios
criterios = ["Knowledge", "Communication", "Experience"]
criterios = ['Precipitação','Elevação','Declividade','Uso e cobertura do solo','Textura do solo',]

n = len(criterios)


st.header("🧠 Método FAHP (Fuzzy AHP)")
st.markdown("Compare os critérios levando em conta a incerteza das avaliações.")

st.markdown("""
**Escala de importância:**
- 1 = Igual importância  
- 3 = Moderada importância  
- 5 = Forte importância  
- 7 = Muito forte importância  
- 9 = Extrema importância  
""")

slider_labels = ['9', '8', '7', '6', '5', '4', '3', '2', '1',
                '1/2', '1/3', '1/4', '1/5', '1/6', '1/7', '1/8', '1/9']  
slider_values = [9, 8, 7, 6, 5, 4, 3, 2, 1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9]


fuzzy_scale = {
    1: (1, 1, 3),
    2: (1, 2, 3),
    3: (1, 3, 5),
    4: (3, 4, 5),
    5: (3, 5, 7),
    6: (5, 6, 7),
    7: (5, 7, 9),
    8: (7, 8, 9),
    9: (7, 9, 9)
}
fuzzy_reciprocal = {k: tuple(round(1 / x, 4) for x in reversed(v)) for k, v in fuzzy_scale.items()}
matriz_fuzzy = np.zeros((n, n, 3))
# Valores para slider (esquerda maior até 1, depois direita maior)

fig, ax = plot_fuzzy_membership(fuzzy_scale)
st.pyplot(fig)


for i in range(n):
    for j in range(i + 1, n):
        key = f"FAHP: {criterios[i]} vs {criterios[j]}"
        col1, col2, col3 = st.columns([2.2, 6, 2.2])
        with col1:
            st.markdown(f"**⬅️ {criterios[i]}**")
        with col2:
            selected_label = st.select_slider(
                f"Comparação entre '{criterios[i]}' e '{criterios[j]}'",
                options=slider_labels,
                value='1',
                key=key,
                help="Valores antes de '1': critério da esquerda é mais importante. Após '1': critério da direita é mais importante."
            )
        with col3:
            st.markdown(f"**{criterios[j]} ➡️**")

        idx = slider_labels.index(selected_label)
        val = slider_values[idx]

        if idx <= slider_labels.index('1'):
            matriz_fuzzy[i, j] = fuzzy_scale[int(val)]
            matriz_fuzzy[j, i] = fuzzy_reciprocal[int(val)]
        else:
            matriz_fuzzy[i, j] = fuzzy_reciprocal[int(round(1 / val))]
            matriz_fuzzy[j, i] = fuzzy_scale[int(round(1 / val))]

    matriz_fuzzy[i, i] = (1, 1, 1)


# === MATRIZ DE COMPARAÇÃO FUZZY ===
st.markdown("### 🧮 Matriz de Comparação Fuzzy (valores médios)")
matriz_media = matriz_fuzzy[:, :, 1]  # Usa o valor médio 'm' de cada TFN
df_matriz_fuzzy = pd.DataFrame(matriz_media, index=criterios, columns=criterios)
st.dataframe(df_matriz_fuzzy, height=250)

# === NORMALIZAÇÃO DA MATRIZ CRISP ===
matriz_crisp = matriz_fuzzy[:, :, 1]  # Extrai apenas o valor médio (m) de cada TFN
sum_cols_crisp = np.sum(matriz_crisp, axis=0)  # Soma das colunas
matriz_norm_crisp = matriz_crisp / sum_cols_crisp  # Normaliza por coluna

# Exibe a matriz normalizada
st.markdown("### 📐 Matriz Normalizada (valores crisp)")
df_norm_crisp = pd.DataFrame(matriz_norm_crisp, index=criterios, columns=criterios)
st.dataframe(df_norm_crisp, height=250)

# === CÁLCULO DOS PESOS FINAIS ===
pesos_crisp = np.mean(matriz_norm_crisp, axis=1)  # Média das linhas
pesos_normalizados = pesos_crisp / np.sum(pesos_crisp)  # Normalização final

# Exibe os pesos finais
st.markdown("### 📊 Pesos Relativos dos Critérios")
df_pesos_fahp = pd.DataFrame({
    "Critério": criterios,
    "Peso Final": np.round(pesos_normalizados, 4)
})
st.dataframe(df_pesos_fahp.set_index("Critério"), height=250)

# === GRÁFICO DE BARRAS DOS PESOS ===
st.markdown("### 📊 Gráfico dos Pesos Relativos") 
import plotly.graph_objects as go

# === GRÁFICO DE BARRAS DOS PESOS (PLOTLY) ===
st.markdown("### 📊 Gráfico Interativo dos Pesos Relativos")

fig_plotly = go.Figure(data=[
    go.Bar(
        x=df_pesos_fahp["Critério"],
        y=df_pesos_fahp["Peso Final"],
        text=[f"{peso:.2f}" for peso in df_pesos_fahp["Peso Final"]],
        textposition="outside",
        marker_color='indianred'
    )
])

fig_plotly.update_layout(
    title="Pesos Relativos dos Critérios (FAHP)",
    xaxis_title="Critérios",
    yaxis_title="Peso",
    xaxis_tickangle=-45,
    height=450,
    margin=dict(l=40, r=40, t=60, b=80)
)

st.plotly_chart(fig_plotly, use_container_width=True)



# === MÉTRICAS DE CONSISTÊNCIA ===
st.markdown("### 📈 Métricas de Consistência (Estimadas para FAHP)")

col_sum_def = np.sum(matriz_crisp, axis=0)  # Usa valores médios
lambda_max_fuzzy = np.dot(col_sum_def, pesos_normalizados)

CI_fuzzy = (lambda_max_fuzzy - n) / (n - 1)

# Tabela real de RI (Índice Aleatório)
RI_dict = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}
RI_fuzzy = RI_dict.get(n, 1.0)  # Usa valor padrão se não encontrado

CR_fuzzy = CI_fuzzy / RI_fuzzy if RI_fuzzy != 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("λ_max (Fuzzy)", f"{lambda_max_fuzzy:.3f}")
c2.metric("CI (Consistência Fuzzy)", f"{CI_fuzzy:.3f}")
c3.metric("CR (Razão de Consistência)", f"{CR_fuzzy:.3f}", delta="OK ✅" if CR_fuzzy < 0.1 else "Ruim ❌")

if CR_fuzzy < 0.1:
    st.success("A matriz fuzzy é considerada consistente. ✅")
else:
    st.warning("A matriz fuzzy pode apresentar inconsistência. ⚠️")
    
if st.button("📥 Exportar Pesos FAHP"):
    df_export = df_pesos_fahp.set_index("Critério")
    st.download_button(
        label="Download CSV",
        data=df_export.to_csv().encode("utf-8"),
        file_name="pesos_fahp.csv",
        mime="text/csv"
    )
