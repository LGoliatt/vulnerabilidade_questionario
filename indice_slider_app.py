import streamlit as st

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



custom_css = """
        <style>
        [data-testid="stTickBarMin"],
        [data-testid="stTickBarMax"] {
            font-size: 0px;
        }
        </style>
        """

# Inject custom CSS with st.markdown()
st.markdown(custom_css, unsafe_allow_html=True)
color = st.select_slider(
    "Select a color of the rainbow",
    options=[
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "indigo",
        "violet",
    ],
)
