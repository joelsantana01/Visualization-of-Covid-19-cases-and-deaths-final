import streamlit as st
from streamlit_option_menu import option_menu

# Configuração da página
st.set_page_config(page_title="Página Principal", page_icon="📊", layout="wide")

# Carregando o Google Fonts (Permanent Marker)
st.markdown("""
    <header>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Permanent+Marker&display=swap" rel="stylesheet">
    </header>
    <style>
        html, body, h1, h2, h3, p, b [class*="css"] {
            font-family: 'Permanent Marker';
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar com o menu de navegação vertical
with st.sidebar:
    choose = option_menu("Menu", ["Home", "Mapas Interativos", "Séries Temporais", "Análises", "Sobre o Autor"],
                         icons=['house', 'map', 'clock', 'bar-chart', 'person'],
                         menu_icon="cast", default_index=1,
                         orientation="vertical",  # Menu vertical dentro da sidebar
                         styles={
                             "container": {"padding": "5!important", "background-color": "#fafafa"},
                             "icon": {"color": "orange", "font-size": "25px"},
                             "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                             "nav-link-selected": {"background-color": "#02ab21"},
                         }, key="menu")

# Conteúdo dinâmico conforme a página selecionada
if choose == "Home":
    st.title("Bem-vindo à Página Principal!")
    st.write("Esta é a página inicial do aplicativo, onde você pode acessar todas as funcionalidades do sistema.")
elif choose == "Mapas Interativos":
    st.title("Mapas Interativos")
    st.write("Visualize e interaja com seus mapas aqui.")
elif choose == "Séries Temporais":
    st.title("Séries Temporais")
    st.write("Aqui você pode analisar gráficos e dados de séries temporais.")
elif choose == "Análises":
    st.title("Análises")
    st.write("Resultados e insights das análises dos seus dados.")
elif choose == "Sobre o Autor":
    st.title("Sobre o Autor")
    st.write("Informações sobre o criador deste aplicativo.")
