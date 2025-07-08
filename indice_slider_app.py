import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Funções auxiliares ===

def triangular(x, a, b, c):
    return np.where(x <= a, 0,
                    np.where(x <= b, (x - a) / (b - a),
                             np.where(x <= c, (c - x) / (c - b), 0)))

def plot_fuzzy_membership(fuzzy_scale, x_range=(0, 10), title="Fuzzy Membership Functions", figsize=(9, 7)):
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

def geometric_mean(matriz_fuzzy, n):
    """ Método geométrico para FAHP """
    prod_linha = np.prod(matriz_fuzzy, axis=1)
    peso_fuzzy = prod_linha ** (1/n)
    return peso_fuzzy

def defuzzify(tfns):
    """ Defuzzifica números fuzzy triangulares pela média ponderada """
    return np.array([(a + 4*b + c)/6 for a, b, c in tfns])

# === Configuração da página ===
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
criterios = ['Precipitação','Elevação','Declividade','Uso e cobertura do solo','Textura do solo']
n = len(criterios)

# === Escala fuzzy e reciprocidade ===
fuzzy_numbers = {
    1:  (1, 1, 3),
    2:  (1, 2, 3),
    3:  (1, 3, 5),
    4:  (3, 4, 5),
    5:  (3, 5, 7),
    6:  (5, 6, 7),
    7:  (5, 7, 9),
    8:  (7, 8, 9),
    9:  (7, 9, 9)
}

# Recíprocos exatos
fuzzy_reciprocal = {
    1: (1/3, 1, 1),
    2: (1/3, 1/2, 1),
    3: (1/5, 1/3, 1),
    4: (1/5, 1/4, 1/3),
    5: (1/7, 1/5, 1/3),
    6: (1/7, 1/6, 1/5),
    7: (1/9, 1/7, 1/5),
    8: (1/9, 1/8, 1/7),
    9: (1/9, 1/9, 1/7)
}

slider_labels = ['9', '8', '7', '6', '5', '4', '3', '2', '1',
                 '1/2', '1/3', '1/4', '1/5', '1/6', '1/7', '1/8', '1/9']  
slider_values = [9, 8, 7, 6, 5, 4, 3, 2, 1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9]

# Mapeamento valor do slider -> número fuzzy
value_to_tfn = {
    '9': fuzzy_numbers[9],
    '8': fuzzy_numbers[8],
    '7': fuzzy_numbers[7],
    '6': fuzzy_numbers[6],
    '5': fuzzy_numbers[5],
    '4': fuzzy_numbers[4],
    '3': fuzzy_numbers[3],
    '2': fuzzy_numbers[2],
    '1': fuzzy_numbers[1],
    '1/2': fuzzy_reciprocal[2],
    '1/3': fuzzy_reciprocal[3],
    '1/4': fuzzy_reciprocal[4],
    '1/5': fuzzy_reciprocal[5],
    '1/6': fuzzy_reciprocal[6],
    '1/7': fuzzy_reciprocal[7],
    '1/8': fuzzy_reciprocal[8],
    '1/9': fuzzy_reciprocal[9]
}

# Inicializa matriz fuzzy
matriz_fuzzy = np.zeros((n, n, 3))

# Interface FAHP
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

fig, ax = plot_fuzzy_membership(fuzzy_numbers)
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

        # Atribuição fuzzy
        if selected_label == '1':
            matriz_fuzzy[i, j] = fuzzy_numbers[1]
            matriz_fuzzy[j, i] = fuzzy_reciprocal[1]
        elif slider_labels.index(selected_label) < slider_labels.index('1'):
            matriz_fuzzy[i, j] = value_to_tfn[selected_label]
            matriz_fuzzy[j, i] = fuzzy_reciprocal[int(slider_values[slider_labels.index(selected_label)])]
        else:
            matriz_fuzzy[j, i] = value_to_tfn[selected_label]
            matriz_fuzzy[i, j] = fuzzy_reciprocal[int(round(1/slider_values[slider_labels.index(selected_label)]))]

    matriz_fuzzy[i, i] = (1, 1, 1)

# === Exibir matriz fuzzy ===
st.markdown("### 🧮 Matriz de Comparação Fuzzy (TFNs)")
df_matriz = pd.DataFrame(index=criterios, columns=criterios)
for i in range(n):
    for j in range(n):
        df_matriz.iloc[i, j] = str(tuple(np.round(matriz_fuzzy[i, j], 2)))
st.dataframe(df_matriz)

# === Cálculo dos pesos fuzzy ===
peso_fuzzy = geometric_mean(matriz_fuzzy, n)
peso_crisp = defuzzify(peso_fuzzy)
peso_normalizado = peso_crisp / np.sum(peso_crisp)

# === Métricas de consistência (AHP clássico) ===
matriz_crisp = matriz_fuzzy[:, :, 1]
sum_cols = np.sum(matriz_crisp, axis=0)
matriz_norm = matriz_crisp / sum_cols
pesos_crsp = np.mean(matriz_norm, axis=1)
lambda_max = np.dot(sum_cols, pesos_crsp)
CI = (lambda_max - n) / (n - 1)
RI_dict = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
RI = RI_dict.get(n, 1.0)
CR = CI / RI if RI != 0 else 0

# === Resultados finais ===
st.markdown("### 📊 Pesos Relativos dos Critérios (FAHP)")
df_pesos = pd.DataFrame({
    "Critério": criterios,
    "Peso Final": np.round(peso_normalizado, 4)
}).set_index("Critério")
st.dataframe(df_pesos)

# === Consistência ===
c1, c2, c3 = st.columns(3)
c1.metric("λ_max", f"{lambda_max:.3f}")
c2.metric("CI", f"{CI:.3f}")
c3.metric("CR", f"{CR:.3f}", delta="OK ✅" if CR < 0.1 else "Ruim ❌")
if CR < 0.1:
    st.success("Matriz consistente.")
else:
    st.warning("Inconsistência detectada. Reavalie suas comparações.")

# === Exportação ===
if st.button("📥 Exportar Pesos FAHP"):
    st.download_button(
        label="Download CSV",
        data=df_pesos.to_csv().encode("utf-8"),
        file_name="pesos_fahp.csv",
        mime="text/csv"
    )