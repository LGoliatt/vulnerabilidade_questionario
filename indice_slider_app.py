import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(page_title="Comparação de Critérios - AHP", layout="centered")

st.title("Análise de Comparação Par a Par")
st.markdown("### Deslize para indicar a importância relativa entre os critérios")

st.info("**Lembre-se:** Se você prefere 'A' a 'B', e 'B' a 'C', então você deve preferir 'A' a 'C' para manter consistência.")

# Função para exibir o slider com descrição intuitiva
def comparacao_criterios(label_a, label_b, key):
    valor = st.slider(
        f"{label_a} vs {label_b}",
        min_value=1,
        max_value=9,
        value=5,
        step=1,
        help=f"1 = {label_a} é igualmente importante a {label_b}, 9 = um dos critérios é extremamente mais importante.",
        key=key
    )
    if valor < 5:
        st.write(f"➡️ **{label_b}** é mais importante que **{label_a}**")
    elif valor > 5:
        st.write(f"➡️ **{label_a}** é mais importante que **{label_b}**")
    else:
        st.write("➡️ **Importância igual** entre os critérios")
    return valor

# Comparações
st.subheader("I. Precipitação x Elevação")
prec_elev = comparacao_criterios("Precipitação", "Elevação", "prec_elev")

st.subheader("II. Precipitação x Declividade")
prec_decliv = comparacao_criterios("Precipitação", "Declividade", "prec_decliv")

st.subheader("III. Precipitação x Uso e cobertura do solo")
prec_uso = comparacao_criterios("Precipitação", "Uso e cobertura do solo", "prec_uso")

st.subheader("IV. Precipitação x Textura do solo")
prec_textura = comparacao_criterios("Precipitação", "Textura do solo", "prec_textura")

st.subheader("V. Elevação x Declividade")
elev_decliv = comparacao_criterios("Elevação", "Declividade", "elev_decliv")

st.subheader("VI. Elevação x Uso e cobertura do solo")
elev_uso = comparacao_criterios("Elevação", "Uso e cobertura do solo", "elev_uso")

st.subheader("VII. Elevação x Textura do solo")
elev_textura = comparacao_criterios("Elevação", "Textura do solo", "elev_textura")

# Exportar os valores
if st.button("Salvar respostas"):
    respostas = {
        "Precipitação x Elevação": prec_elev,
        "Precipitação x Declividade": prec_decliv,
        "Precipitação x Uso e cobertura do solo": prec_uso,
        "Precipitação x Textura do solo": prec_textura,
        "Elevação x Declividade": elev_decliv,
        "Elevação x Uso e cobertura do solo": elev_uso,
        "Elevação x Textura do solo": elev_textura
    }
    st.success("Respostas salvas com sucesso!")
    st.json(respostas)



#==============================================

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
        valor = st.selectbox(
            f"Quanto mais importante é '{criterios[i]}' comparado a '{criterios[j]}'?",
            options=[1, 2, 3, 4, 5, 6, 7, 8, 9],
            index=4,
            key=key
        )
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

