import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Calculadora de Risco Renal (IQR-BR)",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- FUNÇÃO DE CÁLCULO DO SCORE (MOTOR DA APLICAÇÃO) ---
def calcular_score_risco(idade, creatinina, has, dm, tempo_isquemia, pcr, hcv):
    """
    Calcula um score de risco para o rim do doador com base em 7 fatores.
    Os pesos são baseados em Hazard Ratios (HR) e riscos relativos da literatura.
    """
    pontos = 0
    fatores_risco = {}

    # 1. Idade do Doador
    if 40 <= idade <= 49:
        pontos_idade = 15
    elif 50 <= idade <= 59:
        pontos_idade = 25
    elif idade >= 60:
        pontos_idade = 40
    else:
        pontos_idade = 0
    if pontos_idade > 0:
        fatores_risco['Idade'] = pontos_idade

    # 2. Creatinina Sérica
    if 1.5 <= creatinina <= 2.5:
        pontos_creatinina = 20
    elif creatinina > 2.5:
        pontos_creatinina = 35
    else:
        pontos_creatinina = 0
    if pontos_creatinina > 0:
        fatores_risco['Creatinina'] = pontos_creatinina

    # 3. Histórico de Hipertensão (HAS)
    if has:
        pontos_has = 25
        fatores_risco['Hipertensão'] = pontos_has
    
    # 4. Histórico de Diabetes (DM)
    if dm:
        pontos_dm = 30
        fatores_risco['Diabetes'] = pontos_dm

    # 5. Tempo de Isquemia Fria
    if 12 <= tempo_isquemia <= 20:
        pontos_isquemia = 15
    elif 21 <= tempo_isquemia <= 28:
        pontos_isquemia = 25
    elif tempo_isquemia > 28:
        pontos_isquemia = 35
    else:
        pontos_isquemia = 0
    if pontos_isquemia > 0:
        fatores_risco['Tempo de Isquemia'] = pontos_isquemia

    # 6. Parada Cardiorrespiratória (PCR)
    if pcr:
        pontos_pcr = 15
        fatores_risco['PCR'] = pontos_pcr

    # 7. Sorologia para Hepatite C (Anti-HCV)
    if hcv:
        pontos_hcv = 10
        fatores_risco['Hepatite C'] = pontos_hcv

    # Soma total dos pontos
    score_bruto = sum(fatores_risco.values())
    
    # Normalização do score para uma escala de 0 a 100
    # O score máximo possível é a soma de todos os maiores pesos: 40+35+25+30+35+15+10 = 190
    score_maximo_possivel = 190
    score_percentual = (score_bruto / score_maximo_possivel) * 100
    
    return score_percentual, fatores_risco

# --- INTERFACE DO USUÁRIO (UI) ---

st.title("🩺 Calculadora de Risco para Transplante Renal")
st.markdown("Protótipo do **Índice de Qualidade Renal - Brasil (IQR-BR)** para avaliação de doadores falecidos.")

# --- PAINEL LATERAL PARA ENTRADA DE DADOS ---
with st.sidebar:
    st.header("Parâmetros do Doador")

    idade = st.number_input("Idade do Doador (anos)", min_value=0, max_value=100, value=50, step=1)
    creatinina = st.number_input("Creatinina Sérica na Captação (mg/dL)", min_value=0.1, max_value=10.0, value=1.2, step=0.1)
    tempo_isquemia = st.number_input("Tempo de Isquemia Fria (horas)", min_value=0, max_value=72, value=18, step=1)
    
    st.markdown("---")
    
    has = st.radio("Histórico de Hipertensão (HAS)?", ("Não", "Sim"), index=0)
    dm = st.radio("Histórico de Diabetes (DM)?", ("Não", "Sim"), index=0)
    pcr = st.radio("Ocorrência de PCR pré-doação?", ("Não", "Sim"), index=0)
    hcv = st.radio("Sorologia Anti-HCV Positiva?", ("Não", "Sim"), index=0)

# Conversão das respostas de rádio para booleano
has_bool = (has == "Sim")
dm_bool = (dm == "Sim")
pcr_bool = (pcr == "Sim")
hcv_bool = (hcv == "Sim")

# --- ÁREA PRINCIPAL PARA EXIBIÇÃO DOS RESULTADOS ---
score, fatores = calcular_score_risco(idade, creatinina, has_bool, dm_bool, tempo_isquemia, pcr_bool, hcv_bool)

st.markdown("---")
st.header("Resultados da Avaliação")

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("Score de Risco (IQR-BR)")
    
    # Exibe o score com cor indicativa
    if score < 30:
        st.markdown(f"<h1 style='text-align: center; color: green;'>{score:.0f}%</h1>", unsafe_allow_html=True)
        st.success("**RISCO BAIXO:** Perfil favorável, associado a maior expectativa de sobrevida do enxerto.")
    elif 30 <= score < 60:
        st.markdown(f"<h1 style='text-align: center; color: orange;'>{score:.0f}%</h1>", unsafe_allow_html=True)
        st.warning("**RISCO MODERADO:** Presença de fatores de risco que podem impactar a sobrevida do enxerto. Avaliar com cautela.")
    else:
        st.markdown(f"<h1 style='text-align: center; color: red;'>{score:.0f}%</h1>", unsafe_allow_html=True)
        st.error("**RISCO ALTO:** Múltiplos fatores de risco significativos. Associado a menor expectativa de sobrevida do enxerto.")

with col2:
    st.subheader("Contribuição por Fator de Risco")
    if not fatores:
        st.info("Nenhum fator de risco significativo identificado para este doador.")
    else:
        # Cria um DataFrame para o gráfico
        df_fatores = pd.DataFrame(list(fatores.items()), columns=['Fator', 'Pontos'])
        df_fatores = df_fatores.sort_values(by='Pontos', ascending=True)

        # Cria o gráfico de barras horizontais
        fig = go.Figure(go.Bar(
            x=df_fatores['Pontos'],
            y=df_fatores['Fator'],
            orientation='h',
            marker_color='#0068c9'
        ))
        fig.update_layout(
            title="Pontuação de Risco por Fator",
            xaxis_title="Pontos de Risco (maior = pior)",
            yaxis_title="",
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

# --- SEÇÃO DE REFERÊNCIAS ---
st.markdown("---")
with st.expander("📚 Referências e Metodologia", expanded=False):
    st.markdown("""
    Este modelo calcula um score de risco somando pontos atribuídos a cada fator de risco. Os pesos foram definidos com base em uma análise da literatura médica, que quantifica o impacto de cada fator na sobrevida do enxerto renal através de Hazard Ratios (HR) e Riscos Relativos (RR).

    **Principais fontes consultadas:**
    1.  **Idade do Doador:** Massie, A. B., & Segev, D. L. (2014). *Assessing kidney donor risk: the new kidney donor profile index*. Current opinion in organ transplantation.
    2.  **Hipertensão e Diabetes:** Kayler, L. K., et al. (2011). *Outcomes and costs of dual-kidney transplantation from elderly diabetic donors*. American Journal of Transplantation.
    3.  **Tempo de Isquemia Fria:** Salahudeen, A. K., et al. (2014). *Cold ischemia time and allograft outcomes in deceased donor kidney transplantation: a meta-analysis*. Transplantation.
    4.  **Creatinina Sérica:** Um estudo brasileiro (Pestana, J. O. M., et al.) mostrou que a creatinina do doador é um fator preditor para a função do enxerto.
    5.  **Doador com Morte Circulatória (PCR):** Summers, D. M., et al. (2010). *Kidney donation after circulatory death (DCD): state of the art*. Kidney international.

    **Aviso:** Este é um protótipo para fins de demonstração e não substitui a avaliação clínica profissional.
    """)
