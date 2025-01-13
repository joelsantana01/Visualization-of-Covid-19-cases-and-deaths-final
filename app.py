import streamlit as st
import folium
import pandas as pd
from geobr import read_municipality
import geopandas as gpd
from unidecode import unidecode
import numpy as np

#obitos =pd.read_csv("obitos2.csv")
obitos =pd.read_csv("obitos_filtrado.csv")
geometrias = gpd.read_file("geometrias.geojson")
casos = pd.read_csv("casos_filtrados.csv")

obitos['DATA DA NOTIFICACAO'] = pd.to_datetime(obitos['DATA DA NOTIFICACAO']).dt.date #tirando a hora da data
casos['DATA DA NOTIFICACAO'] = pd.to_datetime(casos['DATA DA NOTIFICACAO'], format='%d/%m/%Y')


municipios = read_municipality(year=2020)
municipios_bahia = municipios[municipios["abbrev_state"] == "BA"]
todos_municipios = pd.DataFrame({"name_muni": ["Todos municípios"], "abbrev_state": ["BA"]})
municipios_bahia = pd.concat([todos_municipios, municipios_bahia], ignore_index=True)

opcoes_idade = ["0 a 10", "11 a 20", "21 a 30", "31 a 40", "41 a 50",
                "51 a 60", "61 a 70", "71 a 80", "81 a 90", "91 a 100", "100+"]

#nome diferente do df_filtrado para não dar problema no merge
geometrias['quantidade_z'] = 0
quartis = np.percentile(geometrias['quantidade_z'], [25, 50, 75])    

st.title("🗺️ MAPAS INTERATIVOS DA COVID-19 NA BAHIA")
st.write("Explore os dados da **COVID-19** de maneira visual e interativa. Personalize seus mapas com filtros específicos e obtenha insights sobre a pandemia na Bahia.")
st.write("**Todos os dados foram pegos no site da Secretaria da Saúde do Estado da Bahia(SESAB)**. Os dados foram atualizados pela última vez em **10/10/2024**.")


st.sidebar.header("Filtros para Personalização")
st.sidebar.write("Ajuste os filtros abaixo para criar um mapa **personalizado**:")

st.header("🔍 O Que Cada Filtro Faz?")
st.write("Primeiramente você irá filtrar de acordo com seu interesse em: **casos** ou **óbitos**")
st.subheader("🦠Casos")
st.write("Aqui você pode filtrar por **ano, data, municípios** e **faixa etária**. Use esses filtros para ajustar os dados de casos de **COVID-19** de acordo com suas preferências.")
st.subheader("⚰️Óbitos")
st.write("Este filtro permite que você selecione dados relacionados aos óbitos por COVID-19, incluindo **ano, data, municípios, faixa etária, se possuia alguma comorbidade ou não, sexo** e **tipo de hospital**. Ajuste conforme necessário.")
st.write("Após personalizar os filtros, basta clicar no botão de **'Submeter'** para visualizar o mapa atualizado com base nas suas escolhas.")


st.header("🌍 Mapa da COVID-19 na Bahia")
st.write("**O mapa abaixo reflete os dados filtrados com base nas suas preferências:**")



#funcoes para obitos

def municipios_selecionados(municipios, obitos):
    if isinstance(municipios, str):  
        municipios = [municipios]

    if 'Todos municípios' not in municipios:
        municipios = [unidecode(m.upper().strip()) for m in municipios if pd.notna(m)]
        municipio_selecionado = obitos[obitos['name_muni'].isin(municipios)]
    else:
        municipio_selecionado = obitos

    return municipio_selecionado

def filtrar_por_idade(municipio_selecionado, idades_selecionadas):
    if idades_selecionadas:
        municipio_selecionado = municipio_selecionado[municipio_selecionado['faixa_etaria'].isin(idades_selecionadas)]
    return municipio_selecionado


def filtrar_por_genero(municipio_selecionado, genero):
    if isinstance(genero, str):  
        genero = [genero]
    if "Masculino" in genero and "Feminino" not in genero:  # Verifica se 'genero' não está vazio ou None
        municipio_selecionado = municipio_selecionado[municipio_selecionado['SEXO'] == 'M']
    elif "Feminino" in genero and "Masculino" not in genero:
        municipio_selecionado = municipio_selecionado[municipio_selecionado['SEXO'] == 'F']
    else:
        municipio_selecionado = municipio_selecionado
    return municipio_selecionado


def filtrar_por_comorbidade(municipio_selecionado,comorbidade): 
    if isinstance(comorbidade, str):  
        comorbidade = [comorbidade]
        
    if "Todas as pessoas" not in comorbidade:
        municipio_selecionado = municipio_selecionado[municipio_selecionado['LISTA COMORBIDADE'].isin(comorbidade)]
    
    else:
        municipio_selecionado = municipio_selecionado

    return municipio_selecionado


def filtrar_por_hospital(municipio_selecionado, Hospital):
    if isinstance(Hospital, str):  
        Hospital = [Hospital]
        
    Hospital = [unidecode(m.upper().strip()) for m in Hospital if pd.notna(m)]   
    municipio_selecionado = municipio_selecionado[municipio_selecionado['TIPO ORGAO'].isin(Hospital)]
        
    return municipio_selecionado


def data(data_inicial, data_final, municipio_selecionado):
    df = municipio_selecionado[(municipio_selecionado['DATA DA NOTIFICACAO'] >= pd.to_datetime(data_inicial)) & 
        (municipio_selecionado['DATA DA NOTIFICACAO'] <= pd.to_datetime(data_final))]
    return df

    
def cor_municipio(feature, quartis):
    quantidade = feature['properties'].get('quantidade', 0)  # Usar 0 se quantidade não existir

    # Atribuir cor com base nos quartis
    if quantidade <= quartis[0]:  # 25% menores quantidades
        return '#F1E0FF'  # Roxo Claro
    elif quartis[0] < quantidade <= quartis[1]:  # Entre 25% e 50%
        return '#D29EFF'  # Roxo Médio Claro
    elif quartis[1] < quantidade <= quartis[2]:  # Entre 50% e 75%
        return '#9B4D98'  # Roxo Médio Escuro
    else:  # 25% maiores quantidades
        return '#5D0071'  # Roxo Escuro



#funcoes para casos
def municipios_selecionados_casos(municipios, casos):
    if isinstance(municipios, str):  
        municipios = [municipios]

    if 'Todos municípios' not in municipios:
        municipios = [unidecode(m.upper().strip()) for m in municipios if pd.notna(m)]
        municipio_selecionado = casos[casos['name_muni'].isin(municipios)]
    else:
        municipio_selecionado = casos

    return municipio_selecionado

def filtrar_por_idade_casos(municipio_selecionado, idades_selecionadas):
    if idades_selecionadas:
        municipio_selecionado = municipio_selecionado[municipio_selecionado['faixa_etaria'].isin(idades_selecionadas)]
    return municipio_selecionado


def filtrar_por_genero_casos(municipio_selecionado, genero):
    if isinstance(genero, str):  
        genero = [genero]
    if "Masculino" in genero and "Feminino" not in genero:
        municipio_selecionado = municipio_selecionado[municipio_selecionado['SEXO'] == 'M']
    elif "Feminino" in genero and "Masculino" not in genero:
        municipio_selecionado = municipio_selecionado[municipio_selecionado['SEXO'] == 'F']
    else:
        municipio_selecionado = municipio_selecionado
    return municipio_selecionado

def data_casos(data_inicial, data_final, municipio_selecionado):
    municipio_selecionado = municipio_selecionado[(municipio_selecionado['DATA DA NOTIFICACAO'] >= pd.to_datetime(data_inicial)) & 
        (municipio_selecionado['DATA DA NOTIFICACAO'] <= pd.to_datetime(data_final))]
    return municipio_selecionado

dados = st.sidebar.selectbox("Deseja filtrar por casos ou óbitos?",['Casos','Óbitos'])



if dados == 'Óbitos':
    
    municipios = st.sidebar.multiselect('Escolha o municipio de interesse: ', municipios_bahia['name_muni'], placeholder= "Clique nas opções")

    data_inicial = st.sidebar.date_input('Data de início (AAAA/MM/DD)')
    data_final = st.sidebar.date_input('Data de fim (AAAA/MM/DD)')
      
    idades_selecionadas = st.sidebar.multiselect("Você deseja mapear por qual intervalo de idades?", opcoes_idade , placeholder= "Clique nas opções")
    
    genero = st.sidebar.multiselect("Selecione o gênero: ", ["Masculino", "Feminino"], placeholder= "Clique nas opções")
    
    comorbidade = st.sidebar.multiselect('A pessoa tinha alguma comorbidade?', ["Sim", "Não","Todas as pessoas"], placeholder= "Clique nas opções")
                                         
    
    Hospital = st.sidebar.multiselect("Qual tipo de hospital?", ["Público","Privado","Filantrópico"], placeholder= "Clique nas opções")
    
    
elif dados == 'Casos':
    
    municipios = st.sidebar.multiselect('Escolha o municipio de interesse: ', municipios_bahia['name_muni'], placeholder= "Clique nas opções")

    data_inicial = st.sidebar.date_input('Data de início (AAAA/MM/DD)')
    data_final = st.sidebar.date_input('Data de fim (AAAA/MM/DD)')
      
    idades_selecionadas = st.sidebar.multiselect("Você deseja mapear por qual intervalo de idades?", opcoes_idade , placeholder= "Clique nas opções")
    
    genero = st.sidebar.multiselect("Selecione o gênero: ", ["Masculino", "Feminino"], placeholder= "Clique nas opções")
    


mapa_bahia = folium.Map(location=[-12.9714, -38.5014], zoom_start=6)

submeter = st.sidebar.button("SUBMETER")

# Aplicar filtros apenas quando o botão for pressionado
if submeter and dados == "Óbitos":
    municipio_selecionado = municipios_selecionados(municipios, obitos)
    municipio_selecionado['DATA DA NOTIFICACAO'] = pd.to_datetime(municipio_selecionado['DATA DA NOTIFICACAO'])
    municipio_selecionado = data(data_inicial, data_final, municipio_selecionado) 
    municipio_selecionado = filtrar_por_idade(municipio_selecionado, idades_selecionadas)
    municipio_selecionado = filtrar_por_genero(municipio_selecionado, genero)
    municipio_selecionado = filtrar_por_comorbidade(municipio_selecionado, comorbidade)
    municipio_selecionado = filtrar_por_hospital(municipio_selecionado, Hospital)
    df_filtrado = municipio_selecionado.groupby('name_muni')['quantidade'].sum().reset_index()
    df_filtrado = geometrias.merge(
        df_filtrado[['name_muni', 'quantidade']], 
        left_on='name_muni', 
        right_on='name_muni', 
        how='left'
    )
    df_filtrado = df_filtrado.fillna(0)
    geometrias = df_filtrado
    quartis = np.percentile(geometrias['quantidade'], [25, 50, 75])

    # Adicionando a camada GeoJson ao mapa
    folium.GeoJson(
    geometrias,
    style_function=lambda feature: {
        'fillColor': cor_municipio(feature, quartis),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['name_muni', 'quantidade'],  # Substitua com os nomes das colunas do seu DataFrame
        aliases=['Município:', 'Quantidade:'],  # Aliases para exibir na tooltip
        localize=True
        
    )
).add_to(mapa_bahia)

elif submeter and dados == "Casos":
    
    municipio_selecionado = municipios_selecionados_casos(municipios, casos)
    municipio_selecionado['DATA DA NOTIFICACAO'] = pd.to_datetime(municipio_selecionado['DATA DA NOTIFICACAO'])
    municipio_selecionado = data_casos(data_inicial, data_final, municipio_selecionado) 
    municipio_selecionado = filtrar_por_idade_casos(municipio_selecionado, idades_selecionadas)
    municipio_selecionado = filtrar_por_genero_casos(municipio_selecionado, genero)
    df_filtrado = municipio_selecionado.groupby('name_muni')['quantidade'].sum().reset_index()
    df_filtrado = geometrias.merge(
        df_filtrado[['name_muni', 'quantidade']], 
        left_on='name_muni', 
        right_on='name_muni', 
        how='left'
    )
    df_filtrado = df_filtrado.fillna(0)
    geometrias = df_filtrado
    quartis = np.percentile(geometrias['quantidade'], [25, 50, 75])

    # Adicionando a camada GeoJson ao mapa
    folium.GeoJson(
    geometrias,
    style_function=lambda feature: {
        'fillColor': cor_municipio(feature, quartis),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['name_muni', 'quantidade'],  # Substitua com os nomes das colunas do seu DataFrame
        aliases=['Município:', 'Quantidade:'],  # Aliases para exibir na tooltip
        localize=True
        
    )
).add_to(mapa_bahia)



# Exibir o mapa
from streamlit_folium import folium_static
folium_static(mapa_bahia, width=725)   


st.header("⚠️ VEJA MAIS:")
st.write("""
Caso deseje, você pode **criar mapas de séries temporais** utilizando os mesmos dados da **COVID-19 na Bahia**. 
Clique no link abaixo para explorar essa funcionalidade:

[👉 Criar Mapas de Séries Temporais](https://www.youtube.com/)
""")
# st_folium não esta funcionando de jeito nenhum
    
    
    
st.header("👨‍💻 SOBRE MIM")
st.write("""Olá, sou **Joel**, estudante da Universidade Federal da Bahia (UFBA) e desenvolvi este site como parte do meu projeto de **Iniciação Científica**. No qual fui orientado pela **Professora Doutora Denise Viola**, do Departamento de Estatística do **Instituto de Matemática e Estatística (IME)** da UFBA.

Este projeto busca trazer mais acessibilidade e compreensão sobre a análise de dados relacionados à **COVID-19**, e foi uma oportunidade incrível de aplicar e expandir meus conhecimentos em Estatística, Ciência de Dados e Visualização Espaço-Temporal.

Caso tenha alguma dúvida ou queira conversar mais sobre o projeto, estou à disposição para contato:

- 📧 **E-mail**: [joeldatascience01@gmail.com](mailto:joeldatascience01@gmail.com)
- 🔗 **LinkedIn**: [linkedin.com/in/joeldatascience](https://www.linkedin.com/in/joeldatascience)
""")
#lembrar de criar o linkedin

# rodapé
