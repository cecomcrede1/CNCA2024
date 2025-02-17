#-------------------
# IMPORTAR BIBLIOTECAS
#-------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

#-------------------
# CONFIGURAR PÁGINA
#-------------------

# Configuração para tela cheia (modo wide)
st.set_page_config(layout="wide", page_title="Análise Educacional", page_icon="📊")

# Adicionando Kanit via CSS no Streamlit
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Kanit', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#-------------------
# CONFIGURAR API
#-------------------

# Carregar variáveis do arquivo .env
load_dotenv()

# Verificação da chave da API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("Erro: Chave da API não encontrada. Verifique o arquivo .env.")
    st.stop()

# Configuração da API da Groq
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}

# Dicionário de usuários e senhas
USERS = {"crede01": "0", "aquiraz": "0", "caucaia": "0", "eusebio": "0", "guaiuba": "0", "itaitinga": "0", "maracanau": "0", "maranguape": "0", "pacatuba": "0"}

# Mapeamento de municípios para usuários
MUNICIPIOS = {"crede01": "Crede 01", "aquiraz": "AQUIRAZ", "caucaia": "CAUCAIA", "eusebio": "EUSEBIO", "guaiuba": "GUAIUBA", "itaitinga": "ITAITINGA", "maracanau": "MARACANAU", "maranguape": "MARANGUAPE", "pacatuba": "PACATUBA"}

# Função para obter análise da IA (com cache)
@st.cache_data
def analise(dados):
    """ Gera uma análise baseada nos dados e no conteúdo do arquivo base.txt """
    try:
        with open("base.txt", "r", encoding="utf-8") as f:
            base_conhecimento = f.read()
    except FileNotFoundError:
        base_conhecimento = ['DCRC_2019_OFICIAL fundamental LP.csv','DCRC_2019_OFICIAL fundamental MT.csv']
    
    prompt = (
        "Os arquivos enviados contêm os resultados da Acerto Total dos ciclos 1, 2 e 3 do programa CNCA\n\n"
        "O AVALIE.CE é um programa voltado para a avaliação e acompanhamento da aprendizagem dos estudantes no Ceará.\n"
        "A Acerto Total reflete o conjunto de habilidades adquiridas pelos estudantes em cada ciclo avaliado.\n\n"
        f"Base de conhecimento: {base_conhecimento}\n\n"
        "Agora, com base nos dados fornecidos, realize uma análise detalhada e traga inferências e sugestões:\n"
        "1. **Comparação entre ciclos:** Destaque diferenças relevantes.\n"
        "2. **Análise das habilidades:** Identifique maiores e menores percentuais de acertos.\n"
        "3. **Acerto Total e defasagem:** Avalie e sugira melhorias.\n"
        "4. **Correlação entre aprendizado e número de avaliados.**\n"
        "5. **Cite os resultados de Defazagem, Aprendzado Intermediário e Aprendizado Adequado e compare os resultados deles nos dois ciclos **\n"
        "6. **Consistência entre disciplinas e possíveis discrepâncias.**\n\n"
        "7. **Estabeleça as correlações das habilidades presentes no CNCA com as ofertadas na planilha DCRC, inferindo também as 'relações intracomponentes'..**\n\n"
        "8. **Com base nos dados fornecidos, gere cinco diferentes sequências didáticas, que possibilitem a execução dos objetos específicos presentes na planilha DCRC para cada habilidade;**\n\n"
        f"Dados: {dados.to_json(orient='records')}"
    )
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Você é um analista de dados especializado na educação do Brasil e do Ceará."},
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0].get("message", {}).get("content", "")
        else:
            print("Resposta da API não contém a chave 'choices':", data)
    else:
        print(f"Erro na API: {response.status_code} - {response.text}")

    return ""

#-------------------
# AUTENTICAÇÃO
#-------------------

# Simulação de autenticação
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.image("logo.png", width=250)
    st.title("Login")
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    
    if st.button("Entrar"):
        if USERS.get(username) == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.session_state["municipio"] = MUNICIPIOS[username]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")
else:
    usuario = st.session_state["username"]
    municipio_usuario = st.session_state["municipio"]
    
    st.write(f"Bem-vindo, {municipio_usuario}!")
    
    st.markdown(
        "<h1 style='font-family: Kanit; font-size: 36px; font-weight: bold;'>CNCA 2024</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='font-family: Kanit; font-size: 30px; font-weight: bold;'>Resultados e Análises</h3>",
        unsafe_allow_html=True
    )
    
    # Adicionar linha divisória
    st.write("---")

#-------------------
# IMPORTA OS DADOS (df)
#-------------------

    df = pd.read_csv("df_final.csv")
    # st.text('df')
    # st.dataframe(df, height=400, width=1000)
    
#-------------------
# FILTROS ()
#-------------------
    
    # Filtrar os dados pelo município
    if municipio_usuario != "Todos":
        df = df[df["Município"] == municipio_usuario]
    
    # Barra lateral com filtros
    st.sidebar.subheader("Filtros")
    etapa_filtro = st.sidebar.selectbox("Selecione a Etapa", df["Etapa"].unique())
    componente_filtro = st.sidebar.selectbox("Selecione o Componente Curricular", df["Componente Curricular"].unique())


    if st.sidebar.button("Aplicar Filtros e Analisar"):
        df_filtrado = df[(df["Etapa"] == etapa_filtro) & (df["Componente Curricular"] == componente_filtro)].copy()
        # st.text('df_filtrado')
        # st.dataframe(df_filtrado, height=400, width=1000)
        
#-------------------
# IMPORTAR BIBLIOTECAS
#-------------------

        if not df_filtrado.empty:
            st.markdown(
                "<h3 style='font-family: Kanit; font-size: 24px; font-weight: bold;'>Acerto Total por Ciclo</h3>",
                unsafe_allow_html=True
            )
            # Filtrar dados do Ciclo 1
            df_ciclo1 = df_filtrado[df_filtrado['Ciclos'] == 1].copy()
            df_ciclo1['Acerto Total'] = pd.to_numeric(df_ciclo1['Acerto Total'], errors='coerce')
            acerto_media1 = df_ciclo1['Acerto Total'].mean()

            df_acerto1 = df_ciclo1[['Acerto Total']].drop_duplicates()
            df_aprendizado1 = df_ciclo1[['Defasagem', 'Aprendizado intermediário', 'Aprendizado adequado']].drop_duplicates()
            df_habilidades1 = df_ciclo1[['Descritor', 'Descrição da Habilidade ', 'Habilidades', 'Percentual de acertos']].drop_duplicates()
            df_avaliados1 = df_ciclo1[['Previstos', 'Avaliados','Participação']].drop_duplicates()

            # Filtrar dados do Ciclo 2
            df_ciclo2 = df_filtrado[df_filtrado['Ciclos'] == 2].copy()
            df_ciclo2['Acerto Total'] = pd.to_numeric(df_ciclo2['Acerto Total'], errors='coerce')
            acerto_media2 = df_ciclo2['Acerto Total'].mean()

            df_acerto2 = df_ciclo2[['Acerto Total']].drop_duplicates()
            df_aprendizado2 = df_ciclo2[['Defasagem', 'Aprendizado intermediário', 'Aprendizado adequado']].drop_duplicates()
            df_habilidades2 = df_ciclo2[['Descritor', 'Descrição da Habilidade ', 'Habilidades', 'Percentual de acertos']].drop_duplicates()
            df_avaliados2 = df_ciclo2[['Previstos', 'Avaliados','Participação']].drop_duplicates()

            # Filtrar dados do Ciclo 3
            df_ciclo3 = df_filtrado[df_filtrado['Ciclos'] == 3].copy()
            df_ciclo3['Acerto Total'] = pd.to_numeric(df_ciclo3['Acerto Total'], errors='coerce')
            acerto_media3 = df_ciclo3['Acerto Total'].mean()  # Corrigido para df_ciclo3

            df_acerto3 = df_ciclo3[['Acerto Total']].drop_duplicates()
            df_aprendizado3 = df_ciclo3[['Defasagem', 'Aprendizado intermediário', 'Aprendizado adequado']].drop_duplicates()
            df_habilidades3 = df_ciclo3[['Descritor', 'Descrição da Habilidade ', 'Habilidades', 'Percentual de acertos']].drop_duplicates()
            df_avaliados3 = df_ciclo3[['Previstos', 'Avaliados','Participação']].drop_duplicates()

            # # Criar abas para exibição
            # tab1, tab2, tab3, tab4 = st.tabs(["Acerto Total", "Aprendizado", "Habilidades", "Avaliados"])
            
            # with tab1:
            #     st.subheader("Acerto Total")
            #     st.dataframe(df_acerto1)
            
            # with tab2:
            #     st.subheader("Aprendizado")
            #     st.dataframe(df_aprendizado1)
            
            # with tab3:
            #     st.subheader("Habilidades")
            #     st.dataframe(df_habilidades1)
            
            # with tab4:
            #     st.subheader("Avaliados")
            #     st.dataframe(df_avaliados1)

            # st.success("Os dados foram processados e estão disponíveis nas abas acima.")
            
            
            
            # # Criar abas para exibição
            # tab1, tab2, tab3, tab4 = st.tabs(["Acerto Total", "Aprendizado", "Habilidades", "Avaliados"])
            
            # with tab1:
            #     st.subheader("Acerto Total")
            #     st.dataframe(df_acerto2)
            
            # with tab2:
            #     st.subheader("Aprendizado")
            #     st.dataframe(df_aprendizado2)
            
            # with tab3:
            #     st.subheader("Habilidades")
            #     st.dataframe(df_habilidades2)
            
            # with tab4:
            #     st.subheader("Avaliados")
            #     st.dataframe(df_avaliados2)

            # st.success("Os dados foram processados e estão disponíveis nas abas acima.")
            
#-----------------------------------------            
# Criar colunas para exibição lado a lado
#----------------------------------------

            col1, col2, col3 = st.columns([0.3,0.3,0.3])
            
            with col1:
                fig1 = go.Figure(go.Indicator(
                    mode="gauge+number", 
                    value=acerto_media1, 
                    title={
                        'text': "Acerto Total - Ciclo 1",
                        'font': {'size': 30, 'family': "Kanit", 'color': "black"}
                    },
                     number={
                        'font': {'size': 100, 'family': "Kanit",  'color': "#111827"}  # Ajuste o tamanho e a cor do número aqui
                    },
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickfont': {'size': 30, 'color': "black"} },
                        'bar': {'color': "#111827"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "black",
                        'steps': [
                            {'range': [0, 30], 'color': '#f68511'},
                            {'range': [30.1, 70], 'color': '#ffce2c'},
                            {'range': [70.1, 100], 'color': '#7e84fa'}],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': acerto_media1}}
                    ))
                # Ajustar o tamanho do gráfico
                fig1.update_layout(
                    width=500,  # Largura reduzida
                    height=400,  # Altura reduzida
                    margin=dict(l=10, r=10, t=30, b=0)  # Reduzindo margens
                )

                st.plotly_chart(fig1)
                
                
                previstos =df_avaliados1["Previstos"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Previstos: {previstos} alunos</h3>",
                unsafe_allow_html=True
            )
                avaliados =df_avaliados1["Avaliados"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Avaliados: {avaliados} alunos</h3>",
                unsafe_allow_html=True
            )
                participacao =df_avaliados1["Participação"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Participação: {participacao} %</h3>",
                unsafe_allow_html=True
            )
            
            with col2:
                fig2 = go.Figure(go.Indicator(
                    mode="gauge+number+delta", 
                    value=acerto_media2, 
                    title={
                        'text': "Acerto Total - Ciclo 2",
                        'font': {'size': 30, 'family': "Kanit", 'color': "black"}
                    },
                     number={
                        'font': {'size': 80,'family': "Kanit", 'color': "#111827"}  # Ajuste o tamanho e a cor do número aqui
                    },
                    delta={"reference": acerto_media1, "increasing": {"color": "green"}, "decreasing": {"color": "red"},"position": "bottom", "font": {"size": 30}},  # Configuração do delta
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickfont': {'size': 30, 'color': "black"} },
                        'bar': {'color': "#111827"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "black",
                        'steps': [
                            {'range': [0, 30], 'color': '#f68511'},
                            {'range': [30.1, 70], 'color': '#ffce2c'},
                            {'range': [70.1, 100], 'color': '#7e84fa'}],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': acerto_media2}}
                    ))
                 # Ajustar o tamanho do gráfico
                fig2.update_layout(
                    width=500,  # Largura reduzida
                    height=400,  # Altura reduzida
                    margin=dict(l=10, r=10, t=30, b=0)  # Reduzindo margens
                )
                st.plotly_chart(fig2)
                
                previstos =df_avaliados2["Previstos"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Previstos: {previstos} alunos</h3>",
                unsafe_allow_html=True
            )
                avaliados =df_avaliados2["Avaliados"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Avaliados: {avaliados} alunos</h3>",
                unsafe_allow_html=True
            )
                participacao =df_avaliados2["Participação"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Participação: {participacao} %</h3>",
                unsafe_allow_html=True
            )
            with col3:
                fig4 = go.Figure(go.Indicator(
                    mode="gauge+number+delta", 
                    value=acerto_media3, 
                    title={
                        'text': "Acerto Total - Ciclo 3",
                        'font': {'size': 30, 'family': "Kanit", 'color': "black"}
                    },
                     number={
                        'font': {'size': 80,'family': "Kanit", 'color': "#111827"}  # Ajuste o tamanho e a cor do número aqui
                    },
                    delta={"reference": acerto_media2, "increasing": {"color": "green"}, "decreasing": {"color": "red"},"position": "bottom", "font": {"size": 30}},  # Configuração do delta
                    gauge = {
                        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickfont': {'size': 30, 'color': "black"} },
                        'bar': {'color': "#111827"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "black",
                        'steps': [
                            {'range': [0, 30], 'color': '#f68511'},
                            {'range': [30.1, 70], 'color': '#ffce2c'},
                            {'range': [70.1, 100], 'color': '#7e84fa'}],
                        'threshold': {
                            'line': {'color': "black", 'width': 4},
                            'thickness': 0.75,
                            'value': acerto_media3}}
                    ))
                 # Ajustar o tamanho do gráfico
                fig4.update_layout(
                    width=500,  # Largura reduzida
                    height=400,  # Altura reduzida
                    margin=dict(l=10, r=10, t=30, b=0)  # Reduzindo margens
                )  
                st.plotly_chart(fig4)
                
                previstos =df_avaliados3["Previstos"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Previstos: {previstos} alunos</h3>",
                unsafe_allow_html=True
            )
                avaliados =df_avaliados3["Avaliados"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Avaliados: {avaliados} alunos</h3>",
                unsafe_allow_html=True
            )
                participacao =df_avaliados3["Participação"].mean()
                st.markdown(
                f"<h3 style='font-family: Kanit; font-size: 20px;text-align: center; font-weight: normal;'>Participação: {participacao} %</h3>",
                unsafe_allow_html=True
            )

            # Adicionar linha divisória
            st.markdown("---")

            # Converter o eixo X para string para garantir que os rótulos sejam reconhecidos corretamente
            df_filtrado['Ciclos'] = df_filtrado['Ciclos'].astype(str)

            # Criar figura
            fig5 = go.Figure()

            # Defasagem
            fig5.add_trace(go.Scatter(
                x=df_filtrado['Ciclos'], 
                y=df_filtrado['Defasagem'],
                mode='lines+markers+text',  # Adiciona os rótulos ao gráfico
                name='Defasagem',
                line=dict(color='#f68511'),
                marker=dict(size=8),
                text=df_filtrado['Defasagem'].astype(str), 
                textposition="top center",
                textfont=dict(family="Kanit", size=16, color="black"),
                cliponaxis=False, 
                showlegend=True  # Garantir que apareça na legenda
            ))

            # Aprendizado Intermediário
            fig5.add_trace(go.Scatter(
                x=df_filtrado['Ciclos'], 
                y=df_filtrado['Aprendizado intermediário'],
                mode='lines+markers+text',
                name='Aprendizado Intermediário',
                line=dict(color='#ffce2c'),
                marker=dict(size=8),
                text=df_filtrado['Aprendizado intermediário'].astype(str),
                textposition="top center",
                textfont=dict(family="Kanit", size=16, color="black"),
                cliponaxis=False, 
                showlegend=True
            ))

            # Aprendizado Adequado
            fig5.add_trace(go.Scatter(
                x=df_filtrado['Ciclos'], 
                y=df_filtrado['Aprendizado adequado'],
                mode='lines+markers+text',
                name='Aprendizado Adequado',
                line=dict(color='#7e84fa'),
                marker=dict(size=8),
                text=df_filtrado['Aprendizado adequado'].astype(str),
                textposition="top center",
                textfont=dict(family="Kanit", size=16, color="black"),
                cliponaxis=False, 
                showlegend=True
            ))

            # Configurar o layout do gráfico
            fig5.update_layout(
                title=dict(text="Aprendizagem por Ciclo", font=dict(family="Kanit", size=25)),
                xaxis=dict(
                    title=dict(text="Ciclo", font=dict(family="Kanit", size=20)),
                    tickfont=dict(size=16),  # Alterando o tamanho dos rótulos no eixo X
                    tickmode='array',
                    tickvals=df_filtrado['Ciclos'].tolist(),  # Garantir que os valores estão no eixo X
                    ticktext=df_filtrado['Ciclos'].tolist()   # Forçar os rótulos a aparecerem
                ),
                
                yaxis=dict(
                    title=dict(text="Percentual (%)", font=dict(family="Kanit", size=20)),
                    range=[0, 100],
                    tickfont=dict(size=20)  # Alterando o tamanho dos rótulos no eixo Y
                ),
                margin=dict(l=0, r=0, t=120, b=10),
                    
                template='plotly_white',
                font=dict(family="Kanit", size=20),
                legend=dict(
                    orientation="v",  # Legenda horizontal
                    yanchor="bottom",  # Alinhar a parte inferior da legenda
                    y=-0.5,  # Elevar a legenda acima do gráfico
                    xanchor="center",
                    x=0,
                    font=dict(size=16)  # Ajustar tamanho da fonte da legenda
                ),
                hoverlabel=dict(
                    font_size=20,
                    font_family="Kanit"
                )
            )
            # Adicionar customdata para o hover
            fig5.update_traces(
                hovertemplate="<b>Ciclo:</b> %{customdata[0]}°<br>",
                customdata=df_filtrado[['Ciclos']].values
            )

            # Exibir o gráfico
            st.plotly_chart(fig5)
            
            
            # Adicionar linha divisória
            st.markdown("---")
            
            st.markdown(
                "<h3 style='font-family: Kanit; font-size: 24px; font-weight: bold;'>Desempenho por Habilidade</h3>",
                unsafe_allow_html=True
            )
            
            df_habilidade1 = df_ciclo1.groupby(
                ['Componente Curricular', 'Descritor', 'Descrição da Habilidade ', 'Etapa', 'Habilidades']
            )['Percentual de acertos'].mean().reset_index()  # Garante que o resultado seja um DataFrame
            # st.text('df_habilidade1')
            # st.dataframe(df_habilidade1, height=400, width=1000)
            
            df_habilidade2 = df_ciclo2.groupby(
                ['Componente Curricular', 'Descritor', 'Descrição da Habilidade ', 'Etapa', 'Habilidades']
            )['Percentual de acertos'].mean().reset_index()  # Garante que o resultado seja um DataFrame
            # st.text('df_habilidade2')
            # st.dataframe(df_habilidade2, height=400, width=1000)
            
            df_habilidade3 = df_ciclo3.groupby(
                ['Componente Curricular', 'Descritor', 'Descrição da Habilidade ', 'Etapa', 'Habilidades']
            )['Percentual de acertos'].mean().reset_index()  # Garante que o resultado seja um DataFrame
            # st.text('df_habilidade2')
            # st.dataframe(df_habilidade2, height=400, width=1000)
            
            fig = go.Figure()

            # Definir um limite de caracteres por linha e quebrar em múltiplas linhas
            df_habilidade1["Descrição Quebrada"] = df_habilidade1["Descrição da Habilidade "].str.wrap(50).str.replace('\n', '<br>')

            fig.add_trace(go.Bar(
                x=df_habilidade1["Descritor"],
                y=df_habilidade1["Percentual de acertos"],
                name="Ciclo 1",
                marker=dict(color='#e46e3c', line=dict(color="black", width=2)),
                text=df_habilidade1["Percentual de acertos"],  # Rótulo do percentual
                textposition='auto',  # Posição automática dos rótulos
                textfont=dict(family="Kanit", size=20, color="black"),  # Tamanho e cor dos rótulos
                hovertemplate="<b>Descritor:</b> %{customdata[0]}<br>"
                            "<b>Descrição:</b> %{customdata[1]}<br>",
                customdata=df_habilidade1[["Descritor", "Descrição Quebrada"]].values  # Usa a versão com quebras de linha
            ))


            df_habilidade2["Descrição Quebrada"] = df_habilidade2["Descrição da Habilidade "].str.wrap(50).str.replace('\n', '<br>')

            fig.add_trace(go.Bar(
                x=df_habilidade2["Descritor"],
                y=df_habilidade2["Percentual de acertos"],
                name="Ciclo 2",
                marker=dict(color='#ffce2c', line=dict(color="black", width=2)),
                text=df_habilidade2["Percentual de acertos"],  # Rótulo do percentual
                textposition='auto',  # Posição automática dos rótulos
                textfont=dict(family="Kanit", size=20, color="black"),  # Tamanho e cor dos rótulos
                hovertemplate="<b>Descritor:</b> %{customdata[0]}<br>"
                            "<b>Descrição:</b> %{customdata[1]}<br>",
                customdata=df_habilidade2[["Descritor", "Descrição Quebrada"]].values  # Usa a versão com quebras de linha
            ))
            
            df_habilidade3["Descrição Quebrada"] = df_habilidade3["Descrição da Habilidade "].str.wrap(50).str.replace('\n', '<br>')

            fig.add_trace(go.Bar(
                x=df_habilidade3["Descritor"],
                y=df_habilidade3["Percentual de acertos"],
                name="Ciclo 3",
                marker=dict(color='#7e84fa', line=dict(color="black", width=2)),
                text=df_habilidade3["Percentual de acertos"],  # Rótulo do percentual
                textposition='auto',  # Posição automática dos rótulos
                textfont=dict(family="Kanit", size=20, color="black"),  # Tamanho e cor dos rótulos
                hovertemplate="<b>Descritor:</b> %{customdata[0]}<br>"
                            "<b>Descrição:</b> %{customdata[1]}<br>",
                customdata=df_habilidade3[["Descritor", "Descrição Quebrada"]].values  # Usa a versão com quebras de linha
            ))

            # Layout do gráfico
            fig.update_layout(
                title=dict(text="Média de Acertos por Habilidade (Descritor)", font=dict(family="Kanit", size=20)),
                
                xaxis=dict(
                    title=dict(text="Habilidade", font=dict(family="Kanit", size=20)),
                    tickfont=dict(size=20)  # Alterando o tamanho dos rótulos no eixo X
                ),
                
                yaxis=dict(
                    title=dict(text="Percentual (%)", font=dict(family="Kanit", size=20)),
                    range=[0, 100],
                    tickfont=dict(size=20)  # Alterando o tamanho dos rótulos no eixo Y
                ),
                barmode="group",
                bargroupgap=0,
                showlegend=True,
                hoverlabel=dict(
                    font_size=20,  # Aumenta o tamanho da fonte no hover
                    font_family="Kanit"
                ),
                #hovermode="x unified",
                paper_bgcolor="white",  # Fundo branco
                plot_bgcolor="white",   # Fundo branco do gráfico
                margin=dict(l=50, r=50, t=50, b=50)  # Margens para exibição correta
            )

            # Exibir o gráfico
            st.plotly_chart(fig)
            
            st.markdown("---")

            st.markdown(
                "<h3 style='font-family: Kanit; font-size: 26px; font-weight: bold;'>Sugestão de Análise</h3>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<h3 style='font-family: Kanit; font-size: 14px; color: red;'>Esta análise é feita por inteligência artificial e está em fase de teste. Verifique se ela faz sentido antes de utilizar!</h3>",
                unsafe_allow_html=True
            )
            
            
            with st.status("Analisando seus dados... Aguarde", expanded=False) as status:
                analise = analise(pd.concat([df_acerto1, df_acerto2,df_aprendizado1,df_aprendizado2,df_avaliados1,df_avaliados2,df_habilidades1,df_habilidades2]))
                st.write(analise)
                status.update(label="", expanded=True)
            
    if st.sidebar.button("Sair"):
        st.session_state["authenticated"] = False
        st.rerun()
