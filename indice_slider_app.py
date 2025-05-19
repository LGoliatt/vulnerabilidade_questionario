import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AHP - Consistência", layout="centered")
st.title("🎯 Consistência na Análise AHP")
st.markdown("Preencha a tabela comparando os critérios **do ponto de vista da linha em relação à coluna**.")

st.markdown("""
**Escala de importância:**
- Valores **positivos** → Linha é mais importante  
- Valores **negativos** → Coluna é mais importante  
- Valor absoluto indica o grau de importância (1 = igual, 9 = extrema)  
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
        valor = st.slider(
            f"Quanto mais importante é '{criterios[i]}' comparado a '{criterios[j]}'?",
            min_value=-9,
            max_value=9,
            value=0,
            step=1,
            key=key,
            help="Valores positivos: critério da linha mais importante. Negativos: critério da coluna mais importante. Zero não é permitido."
        )

        # Impedir seleção de zero
        if valor == 0:
            st.warning("O valor 0 não é permitido em AHP. Selecione de -9 a -1 ou 1 a 9.")
        else:
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

# RI (Índice Aleatório)
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
