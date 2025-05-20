import streamlit as st
import pandas as pd
import numpy as np
 
st.set_page_config(page_title="AHP - Consistência", layout="centered")
st.title("🎯 Consistência na Análise AHP")
st.markdown("Preencha a tabela comparando os critérios **do ponto de vista da linha em relação à coluna**.")

st.markdown("""
**Escala de importância:**
- 1 = Igual importância  
- 3 = Moderada importância  
- 5 = Forte importância  
- 7 = Muito forte importância  
- 9 = Extrema importância  
""")

# Critérios a serem comparados
criterios = ["Knowledge", "Communication", "Experience"]
n = len(criterios)

# Inicializa a matriz
matriz = np.ones((n, n))
entrada_usuario = {}

# Geração dos pares (só metade da matriz superior)
for i in range(n):
    for j in range(i + 1, n):
        key = f"{criterios[i]} vs {criterios[j]}"

        # Valores e rótulos para o slider: 1/9 a 9, exceto 0
        slider_labels = ['9', '8', '7', '6', '5', '4', '3', '2', '1',
                         '2', '3', '4', '5', '6', '7', '8', '9']
        slider_values = [9, 8, 7, 6, 5, 4, 3, 2, 1,
                         2, 3, 4, 5, 6, 7, 8, 9]

        col1, col2, col3 = st.columns([2.0, 6, 2.0])
        with col1:
            st.markdown(f"**⬅️ {criterios[i]}**")
        with col2:
            idx = slider_labels.index('1')  # posição inicial do slider
            selected_label = st.select_slider(
                f"Comparação entre '{criterios[i]}' e '{criterios[j]}'",
                options=slider_labels,
                value=slider_labels[idx],
                key=key,
                help="Valores maiores: mais importância para o critério da esquerda. Frações: mais importância para o critério da direita."
            )
        with col3:
            st.markdown(f"**{criterios[j]} ➡️**")

        # Converte rótulo selecionado para valor numérico
        valor = slider_values[slider_labels.index(selected_label)]

        entrada_usuario[key] = valor
        matriz[i, j] = valor
        matriz[j, i] = round(1 / valor, 3)



# Exibir a matriz preenchida
st.markdown("### 🧮 Matriz de Comparação")
df_matriz = pd.DataFrame(matriz, index=criterios, columns=criterios)
st.dataframe(df_matriz, height=250)

# Normalização da matriz e cálculo dos pesos
st.markdown("### 📊 Pesos Relativos dos Critérios")
col_sum = matriz.sum(axis=0)
matriz_normalizada = matriz / col_sum
pesos = matriz_normalizada.mean(axis=1)
df_pesos = pd.DataFrame({
    "Critério": criterios,
    "Peso": pesos
})
st.dataframe(df_pesos.set_index("Critério"), height=200)

# Verificação de consistência
st.markdown("### ✅ Índice de Consistência (CI)")

# Cálculo de λ_max
lambda_max = np.dot(col_sum, pesos)
CI = (lambda_max - n) / (n - 1)

# RI (Índice Aleatório) para diferentes tamanhos de matriz (até n = 10)
RI_dict = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
           6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
RI = RI_dict[n]
CR = CI / RI if RI != 0 else 0



st.markdown("### 📈 Métricas de Consistência")
# st.write(f"λ_max: {lambda_max:.3f}")
# st.write(f"Índice de Consistência (CI): {CI:.3f}")
# st.write(f"Razão de Consistência (CR): {CR:.3f}")

col1, col2, col3 = st.columns(3)
col1.metric("λ_max", f"{lambda_max:.3f}")
col2.metric("CI (Índice de Consistência)", f"{CI:.3f}")
col3.metric("CR (Razão de Consistência)", f"{CR:.3f}", delta="OK ✅" if CR < 0.1 else "Ruim ❌")


if CR < 0.1:
    st.success("A matriz de comparação é consistente! ✅")
else:
    st.error("A matriz de comparação é inconsistente. ❌ Reavalie suas comparações.")

# Exportar resultados
if st.button("📥 Exportar como CSV"):
    df_export = df_pesos.set_index("Critério")
    st.download_button(
        label="Download Pesos como CSV",
        data=df_export.to_csv().encode("utf-8"),
        file_name="pesos_ahp.csv",
        mime="text/csv"
    )
