import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Índice de vulnerabilidade hídrica natural em bacias hidrográficas", layout="centered")
st.title("📊 Índice de vulnerabilidade hídrica natural em bacias hidrográficas")
st.markdown(
'''
O presente estudo utiliza a metodologia **AHP** para desenvolver um **índice 
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


# Tabs
#tab1, tab2 = st.tabs(["📐 AHP", "🧠 FAHP (Fuzzy AHP)"])

# ---------------------------
# TAB 1 - AHP
# ---------------------------
#with tab1:
st.header("📐 Método AHP (Analytic Hierarchy Process)")
st.markdown("Compare os critérios com base em sua importância relativa.")
st.markdown("""
**Escala de importância:**
- 1 = Igual importância  
- 3 = Moderada importância  
- 5 = Forte importância  
- 7 = Muito forte importância  
- 9 = Extrema importância  
""")

matriz = np.ones((n, n))
entrada_usuario = {}

slider_labels = ['9', '8', '7', '6', '5', '4', '3', '2', '1',
            '2', '3', '4', '5', '6', '7', '8', '9']  
slider_values = [9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9]



for i in range(n):
    for j in range(i + 1, n):
        key = f"AHP: {criterios[i]} vs {criterios[j]}"
        col1, col2, col3 = st.columns([2.2, 6, 2.2])
        with col1:
            st.markdown(f"**⬅️ {criterios[i]}**")
        with col2:
            idx = slider_labels.index('1')
            selected_label = st.select_slider(
                f"Comparação entre '{criterios[i]}' e '{criterios[j]}'",
                options=slider_labels,
                value=slider_labels[idx],
                key=key,
                help="Valores maiores: mais importância para o critério da esquerda. Frações: mais importância para o critério da direita."
            )
        with col3:
            st.markdown(f"**{criterios[j]} ➡️**")

        valor = slider_values[slider_labels.index(selected_label)]
        entrada_usuario[key] = valor
        matriz[i, j] = valor
        matriz[j, i] = round(1 / valor, 3)

st.markdown("### 🧮 Matriz de Comparação")
df_matriz = pd.DataFrame(matriz, index=criterios, columns=criterios)
st.dataframe(df_matriz, height=250)

st.markdown("### 📊 Pesos Relativos dos Critérios")
col_sum = matriz.sum(axis=0)
matriz_normalizada = matriz / col_sum
pesos = matriz_normalizada.mean(axis=1)
df_pesos = pd.DataFrame({
    "Critério": criterios,
    "Peso": pesos
})
st.dataframe(df_pesos.set_index("Critério"), height=200)

st.markdown("### 📈 Métricas de Consistência")
lambda_max = np.dot(col_sum, pesos)
CI = (lambda_max - n) / (n - 1)
RI_dict = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
           6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
RI = RI_dict[n]
CR = CI / RI if RI != 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("λ_max", f"{lambda_max:.3f}") 
col2.metric("CI (Índice de Consistência)", f"{CI:.3f}")
col3.metric("CR (Razão de Consistência)", f"{CR:.3f}", delta="OK ✅" if CR < 0.1 else "Ruim ❌")

if CR < 0.1:
    st.success("A matriz de comparação é consistente! ✅")
else:
    st.error("A matriz de comparação é inconsistente. ❌ Reavalie suas comparações.")

if st.button("📥 Exportar Pesos AHP"):
    df_export = df_pesos.set_index("Critério")
    st.download_button(
        label="Download CSV",
        data=df_export.to_csv().encode("utf-8"),
        file_name="pesos_ahp.csv",
        mime="text/csv"
    )
