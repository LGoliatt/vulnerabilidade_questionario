
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import json
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#fucm efnb edfc ftbu

def enviar_email(resposta):
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "goliatt@gmail.com"
    app_password = "fucmefnbedfcftbu"  # 🔐 Senha de app (16 caracteres, sem espaços)

    #app_password = st.secrets["gmail_app_password"]
    #sender_email = st.secrets["gmail_user"]

    recipient_email = "goliatt@gmail.com"  # ou outro e-mail seu

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = "Nova resposta no questionário FAHP - "+resposta['saved_at_local']

    body = f"Resposta recebida:\n\n{resposta}"
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Ativa criptografia
        server.login(sender_email, app_password)  # Usa a senha de app
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
    
def plot_pesos_fahp_plotly(df_pesos: pd.DataFrame, titulo="Pesos Relativos dos Critérios (FAHP)"):
    """
    Gera um gráfico de barras interativo Plotly para os pesos dos critérios.

    Parâmetros:
        df_pesos (pd.DataFrame): DataFrame contendo as colunas 'Critério' e 'Peso Final'.
        titulo (str): Título do gráfico.

    Retorna:
        fig (go.Figure): Figura do Plotly pronta para ser exibida.
    """
    fig = go.Figure(data=[
        go.Bar(
            x=df_pesos["Critério"],
            y=df_pesos["Peso Final"],
            text=[f"{peso:.3f}" for peso in df_pesos["Peso Final"]],
            textposition="outside",
            marker_color='indianred'
        )
    ])

    fig.update_layout(
        title=titulo,
        xaxis_title="Critérios",
        yaxis_title="Peso",
        xaxis_tickangle=-45,
        height=450,
        margin=dict(l=40, r=40, t=60, b=80),
        legend=dict(orientation="h")
    )

    return fig


def plot_fuzzy_membership_plotly(fuzzy_scale, x_range=(0, 10), title="Funções de Pertinência Fuzzy"):
    """
    Plota funções de pertinência fuzzy triangulares usando Plotly.

    Parâmetros:
        fuzzy_scale (dict): Dicionário com os conjuntos fuzzy no formato {nível: (a, b, c)}.
        x_range (tuple): Intervalo de valores de x para plotagem (início, fim).
        title (str): Título do gráfico.

    Retorna:
        fig (plotly.graph_objects.Figure): Figura pronta para exibição com Streamlit.
    """
    def triangular(x, a, b, c):
        return np.where(x <= a, 0,
                        np.where(x <= b, (x - a) / (b - a),
                                 np.where(x <= c, (c - x) / (c - b), 0)))

    x = np.linspace(*x_range, 500)
    fig = go.Figure()

    for label, (a, b, c) in fuzzy_scale.items():
        y = triangular(x, a, b, c)
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name=f"Nível {label} ({a}, {b}, {c})",
            fill='tozeroy',
            hovertemplate=f"Nível {label}<br>a={a}, b={b}, c={c}<br>x=%{{x:.2f}}<br>μ=%{{y:.2f}}<extra></extra>",
            opacity=0.4
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Valor de entrada",
        yaxis_title="Grau de Pertinência",
        height=500,
        legend_title="Escalas Triangulares",
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(range=[x_range[0], x_range[1]]),
        yaxis=dict(range=[0, 1.05])
    )

    return fig


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



st.header("📝 Perfil do Respondente")

# Opções solicitadas
idade_opts = [
    "— Selecione —",
    "De 18 a 24 anos",
    "De 25 a 44 anos",
    "De 45 a 64 anos",
    "De 65 a 74 anos",
    "Mais de 74 anos",
]
area_opts = [
    "— Selecione —",
    "Engenharia",
    "Utilidades",
    "Meio Ambiente",
    "Sistemas ou Tecnologia da Informação",
    "Marketing ou Divulgação",
    "Gestão",
    "Outros",
]

st.markdown("**Para nos ajudar a segmentar os dados, por favor responda às seguintes perguntas:**")

idade_sel = st.selectbox("Idade *", idade_opts, index=0, help="Campo obrigatório.")
area_sel = st.selectbox("Área de atuação *", area_opts, index=0, help="Campo obrigatório.")
area_outros = ""
if area_sel == "Outros":
    area_outros = st.text_input("Se você marcou 'Other:', especifique *", max_chars=80)
    


st.header("📝 Contexto da Pesquisa")
 
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
#criterios = ["A1", "A2", "A3"]

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

# Definição da escala de importância com rótulos descritivos
importancia_labels = [
    "9 - Extrema (à esquerda)",
    "8 - Entre muito forte à extrema (à esquerda)",
    "7 - Muito forte (à esquerda)",
    "6 - Entre forte à muito forte (à esquerda)",
    "5 - Forte (à esquerda)",
    "4 - Entre moderada à forte (à esquerda)",
    "3 - Moderada (à esquerda)",
    "2 - Entre igual à moderada (à esquerda)",
    "1 - Igual importância",
    "1/2 - - Entre igual à moderada (à direita)",
    "1/3 - Moderada (à direita)",
    "1/4 - Entre moderada à forte (à direita)",
    "1/5 - Forte (à direita)",
    "1/6 - Entre forte à muito forte (à direita)",
    "1/7 - Muito forte (à direita)",
    "1/8 - Entre muito forte à extrema (à direita)",
    "1/9 - Extrema (à direita)"
]


# Dicionário para mapear cada rótulo ao seu valor numérico
label_to_value = dict(zip(importancia_labels, slider_values))


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

#fig = plot_fuzzy_membership_plotly(fuzzy_scale)
#st.plotly_chart(fig, use_container_width=True)


for i in range(n):
    for j in range(i + 1, n):
        key = f"FAHP: {criterios[i]} vs {criterios[j]}"
        col1, col2, col3 = st.columns([2.2, 6, 2.2])
        with col1:
            st.markdown(f"**⬅️ {criterios[i]}**")
        with col2:
            selected_label = st.select_slider(
                f"Comparação entre '{criterios[i]}' e '{criterios[j]}'",
                options=importancia_labels,
                value="1 - Igual importância",
                key=key,
                help="Selecione a importância relativa entre os critérios."
            )
        with col3:
            st.markdown(f"**{criterios[j]} ➡️**")

        # Obtem o valor numérico correspondente ao rótulo selecionado
        val = label_to_value[selected_label]
        idx = importancia_labels.index(selected_label)

        if idx <= importancia_labels.index("1 - Igual importância"):
            # Critério à esquerda é mais importante ou igual
            matriz_fuzzy[i, j] = fuzzy_scale[int(round(val))]
            matriz_fuzzy[j, i] = fuzzy_reciprocal[int(round(val))]
        else:
            # Critério à direita é mais importante
            matriz_fuzzy[i, j] = fuzzy_reciprocal[int(round(1 / val))]
            matriz_fuzzy[j, i] = fuzzy_scale[int(round(1 / val))]

    matriz_fuzzy[i, i] = (1, 1, 1)
    

# === MATRIZ DE COMPARAÇÃO FUZZY ===
#st.markdown("### 🧮 Matriz de Comparação Fuzzy (valores médios)")
matriz_media = matriz_fuzzy[:, :, 1]  # Usa o valor médio 'm' de cada TFN
df_matriz_fuzzy = pd.DataFrame(matriz_media, index=criterios, columns=criterios)
#st.dataframe(df_matriz_fuzzy, height=250)

# === NORMALIZAÇÃO DA MATRIZ CRISP ===
matriz_crisp = matriz_fuzzy[:, :, 1]  # Extrai apenas o valor médio (m) de cada TFN
sum_cols_crisp = np.sum(matriz_crisp, axis=0)  # Soma das colunas
matriz_norm_crisp = matriz_crisp / sum_cols_crisp  # Normaliza por coluna

# Exibe a matriz normalizada
#st.markdown("### 📐 Matriz Normalizada (valores crisp)")
df_norm_crisp = pd.DataFrame(matriz_norm_crisp, index=criterios, columns=criterios)
#st.dataframe(df_norm_crisp, height=250)

# === CÁLCULO DOS PESOS FINAIS ===
pesos_crisp = np.mean(matriz_norm_crisp, axis=1)  # Média das linhas
pesos_normalizados = pesos_crisp / np.sum(pesos_crisp)  # Normalização final

# Exibe os pesos finais
#st.markdown("### 📊 Pesos Relativos dos Critérios")
df_pesos_fahp = pd.DataFrame({
    "Critério": criterios,
    "Peso Final": np.round(pesos_normalizados, 4)
})
#st.dataframe(df_pesos_fahp.set_index("Critério"), height=250)

# === GRÁFICO DE BARRAS DOS PESOS ===
st.markdown("### 📊 Gráfico dos Pesos Relativos") 
fig_plotly = plot_pesos_fahp_plotly(df_pesos_fahp)
st.plotly_chart(fig_plotly, use_container_width=True)


# === MÉTRICAS DE CONSISTÊNCIA ===
st.markdown("### 📈 Métricas de Consistência (Estimadas para FAHP)")
st.markdown("""
💡 **Nota sobre a Razão de Consistência (CR):**  
Para que a matriz de comparação seja considerada **consistentente aceitável**, 
o valor de **CR deve ser menor que 0.1**. Valores acima disso indicam possíveis 
inconsistências nas avaliações feitas e sugerem revisão das comparações pareadas.
""")

col_sum_def = np.sum(matriz_crisp, axis=0)  # Usa valores médios
#st.dataframe(col_sum_def)
#st.dataframe(pesos_normalizados)
#lambda_max_fuzzy = np.dot(col_sum_def, pesos_normalizados) 

lambda_max_fuzzy = abs(np.linalg.eigvals(df_matriz_fuzzy)).max()
#st.subheader("Maior Autovalor (em valor absoluto):")
#st.metric(label="λ_max", value=f"{lambda_max_fuzzy:.4f}")

CI_fuzzy = (lambda_max_fuzzy - n) / (n - 1)

# Tabela real de RI (Índice Aleatório)
RI_dict = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
}
RI_fuzzy = RI_dict.get(n, 1.0)  # Usa valor padrão se não encontrado

CR_fuzzy = CI_fuzzy / RI_fuzzy if RI_fuzzy != 0 else 0

c1, c2, c3 = st.columns(3)
#c1.metric("λ_max (Fuzzy)", f"{lambda_max_fuzzy:.3f}")
#c2.metric("CI (Consistência Fuzzy)", f"{CI_fuzzy:.3f}")
#c3.metric("CR (Razão de Consistência)", f"{CR_fuzzy:.3f}", delta="OK ✅" if CR_fuzzy < 0.1 else "Ruim ❌")
c1.metric("CR (Razão de Consistência)", f"{CR_fuzzy:.3f}", delta="OK ✅" if CR_fuzzy < 0.1 else "Ruim ❌")


CR_OK = CR_fuzzy < 0.1
CR_count = 0
if CR_OK:    
    st.success("A matriz fuzzy é considerada consistente. ✅")
else:
    CR_count+=1
    st.warning("⚠️ A matriz fuzzy pode apresentar inconsistência. ⚠️ Por favor revise as comparações.")
    

    
#if st.button("📥 Exportar Pesos FAHP"):
#    df_export = df_pesos_fahp.set_index("Critério")
#    st.download_button(
#        label="Download CSV",
#        data=df_export.to_csv().encode("utf-8"),
#        file_name="pesos_fahp.csv",
#        mime="text/csv"
#    )


    
with st.form("enviar_resposta"):
    st.markdown("**Clique aqui para submeter sua resposta**")
    
    st.markdown("---")
    st.markdown("**Feedback de usabilidade** (opcional)")
    dificuldade_texto = st.text_area(
           "Você teve dificuldade para avaliar algum item do formulário? Qual ou quais itens? Quais as dificuldades?",
           placeholder="Descreva aqui eventuais dificuldades encontradas...",
           height=120
       )
    sugestao_texto = st.text_area(
           "Gostaria de fazer alguma sugestão? Qual ou quais?",
           placeholder="Compartilhe aqui suas sugestões de melhoria...",
           height=120
       )
    
    # Botão de submissão do formulário
    submitted = st.form_submit_button("Enviar resposta")


# Processamento da submissão
if submitted:
    # Validações mínimas
    erros = []
    if idade_sel == "— Selecione —":
        erros.append("• Selecione uma faixa de **Idade**.")
    if area_sel == "— Selecione —":
        erros.append("• Selecione a **Área de atuação**.")
    if area_sel == "Outros" and not area_outros.strip():
        erros.append("• Especifique a **Área de atuação** quando selecionar 'Outros'.")


    if erros:
        st.error("Não foi possível registrar a resposta:\n\n" + "\n".join(erros))
    else:
        # Timestamps
        tz = ZoneInfo("America/Sao_Paulo")
        now_local = datetime.now(tz)
        now_utc = datetime.utcnow()

        # Monta o payload da resposta
        resposta = {
            "saved_at_local": now_local.isoformat(timespec="seconds"),
            "saved_at_utc": now_utc.isoformat(timespec="seconds") + "Z",
            "idade": idade_sel,
            "area_atuacao": (area_outros.strip() if area_sel == "Other:" else area_sel),

            # Perguntas abertas (opcionais)
            "dificuldade_avaliacao": dificuldade_texto.strip() if dificuldade_texto else None,
            "sugestoes": sugestao_texto.strip() if sugestao_texto else None,

            # Itens do FAHP atuais (úteis para análises por segmento)
            "criterios": criterios,
            "pesos_fahp": df_pesos_fahp.to_dict(orient="records"),
            "CR_fuzzy": float(CR_fuzzy),
            "lambda_max": float(np.real_if_close(lambda_max_fuzzy)),
            "matriz_comparacao_media": {
                "index": list(df_matriz_fuzzy.index),
                "columns": list(df_matriz_fuzzy.columns),
                "values": df_matriz_fuzzy.values.tolist(),
            },
        }

        # Persistência: 1 arquivo por resposta
        os.makedirs("respostas", exist_ok=True)
        uid = uuid.uuid4().hex[:6]
        fname = f"respostas/resposta_{now_local.strftime('%Y%m%d-%H%M%S')}_{uid}.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(resposta, f, ensure_ascii=False, indent=2)

        st.success(f"Resposta registrada com sucesso em **{fname}**.")
        st.caption(
            f"Registro efetuado em {now_local.strftime('%d/%m/%Y %H:%M:%S')} (America/Sao_Paulo) "
            f"| UTC: {now_utc.strftime('%Y-%m-%d %H:%M:%S')}Z"
        )

        # Facilita exportar a mesma resposta como download imediato
        st.download_button(
            label="⬇️ Baixar esta resposta (JSON)",
            data=json.dumps(resposta, ensure_ascii=False, indent=2),
            file_name=os.path.basename(fname),
            mime="application/json",
        )
        
        enviar_email(resposta)     
            
             
#%%      
  