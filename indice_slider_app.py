import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AHP e FAHP", layout="centered")
st.title("📊 AHP vs FAHP")
st.markdown("Compare e avalie pesos de critérios com métodos clássico (AHP) e fuzzy (FAHP).")

# Critérios
criterios = ["Knowledge", "Communication", "Experience"]
criterios = ['Precipitação','Elevação','Declividade','Uso e cobertura do solo','Textura do solo',]

n = len(criterios)

# Tabs
tab1, tab2 = st.tabs(["📐 AHP", "🧠 FAHP (Fuzzy AHP)"])

# ---------------------------
# TAB 1 - AHP
# ---------------------------
with tab1:
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
                     '1/2', '1/3', '1/4', '1/5', '1/6', '1/7', '1/8', '1/9']
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
            matriz[j, i] = round(1./ valor, 3)

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

# ---------------------------
# TAB 2 - FAHP
# ---------------------------
with tab2:
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

    fuzzy_scale = {
        1: (1, 1, 1),
        2: (1, 2, 3),
        3: (2, 3, 4),
        4: (3, 4, 5),
        5: (4, 5, 6),
        6: (5, 6, 7),
        7: (6, 7, 8),
        8: (7, 8, 9),
        9: (8, 9, 9)
    }
    fuzzy_reciprocal = {k: tuple(round(1 / x, 4) for x in reversed(v)) for k, v in fuzzy_scale.items()}
    matriz_fuzzy = np.zeros((n, n, 3))
    # Valores para slider (esquerda maior até 1, depois direita maior)
    slider_labels = ['9', '8', '7', '6', '5', '4', '3', '2', '1',
                     '2', '3', '4', '5', '6', '7', '8', '9']
    slider_values = [9, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    

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

    # === MATRIZ DE COMPARAÇÃO ===
    st.markdown("### 🧮 Matriz de Comparação (valores médios dos TFNs)")
    matriz_media = np.round(matriz_fuzzy[:, :, 1], 3)
    df_matriz_fuzzy = pd.DataFrame(matriz_media, index=criterios, columns=criterios)
    st.dataframe(df_matriz_fuzzy, height=250)

    # === CÁLCULO DE PESOS FUZZY ===
    sum_cols = np.sum(matriz_fuzzy, axis=0)
    norm_fuzzy = np.zeros((n, n, 3))
    for i in range(n):
        for j in range(n):
            norm_fuzzy[i, j] = (
                matriz_fuzzy[i, j, 0] / sum_cols[j, 2],
                matriz_fuzzy[i, j, 1] / sum_cols[j, 1],
                matriz_fuzzy[i, j, 2] / sum_cols[j, 0]
            )

    soma_linhas = np.sum(norm_fuzzy, axis=1)
    pesos_defuzzificados = [(l + m + u) / 3 for l, m, u in soma_linhas]
    pesos_normalizados = pesos_defuzzificados / np.sum(pesos_defuzzificados)

    # === PESOS RELATIVOS ===
    st.markdown("### 📊 Pesos Relativos dos Critérios")
    df_pesos_fahp = pd.DataFrame({
        "Critério": criterios,
        "Peso Fuzzy": [f"{tuple(np.round(x*1.0, 3))}" for x in soma_linhas],
        "Peso Final": np.round(pesos_normalizados, 4)
    })
    st.dataframe(df_pesos_fahp.set_index("Critério"), height=250)

    # === MÉTRICAS DE CONSISTÊNCIA ===
    st.markdown("### 📈 Métricas de Consistência (Estimadas para FAHP)")
    col_sum_def = np.sum(matriz_fuzzy[:, :, 1], axis=0)  # valor médio (m)
    lambda_max_fuzzy = np.dot(col_sum_def, pesos_normalizados)
    CI_fuzzy = (lambda_max_fuzzy - n) / (n - 1)
    RI_fuzzy = RI_dict[n]
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