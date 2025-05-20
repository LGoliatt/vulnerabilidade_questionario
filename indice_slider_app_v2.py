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
criterios = ["Knowledge", "Communication Skill", "Experience"]
n = len(criterios)

# Inicializa a matriz
matriz = np.ones((n, n))
entrada_usuario = {}

# Geração dos pares (só metade da matriz superior)
for i in range(n):
    for j in range(i + 1, n):
        key = f"{criterios[i]} vs {criterios[j]}"
        options = [i for i in range(-9, 10) if i != 0]  # valores de -9 a +9, excluindo 0

        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            st.markdown(f"**⬅️ {criterios[i]}**")
        with col2:
            valor = st.radio(
                f"Comparação entre '{criterios[i]}' e '{criterios[j]}'",
                options=options,
                index=options.index(1),
                horizontal=True,
                key=key,
                help="Valores positivos: critério à esquerda é mais importante. Negativos: critério à direita é mais importante."
            )
        with col3:
            st.markdown(f"**{criterios[j]} ➡️**")

        entrada_usuario[key] = valor
        matriz[i, j] = abs(valor) if valor > 0 else round(1 / abs(valor), 3)
        matriz[j, i] = round(1 / matriz[i, j], 3)

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

st.write(f"λ_max: {lambda_max:.3f}")
st.write(f"Índice de Consistência (CI): {CI:.3f}")
st.write(f"Razão de Consistência (CR): {CR:.3f}")

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
