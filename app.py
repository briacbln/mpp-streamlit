from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from matplotlib.collections import BrokenBarHCollection
import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import altair as alt
import math 
import plotly.express as px 

st.set_page_config(
    page_title = "Offre - MPP",
    page_icon = "📈",
    layout = "wide"
)

# st.title("Dashboard Pôle Offre 💚")

# def space(num_lines=1):


listeIsin = [
    ["FR0010135103", "Carmignac Patrimoine A EUR Acc"],
    ["LU1694789535", "DNCA Invest Alpha Bonds B EUR Acc"],
    ["FR0010687053", "Dorval Global Convictions R"],
    ["FR0012355139", "Lazard Patrimoine SRI RC EUR"],
    ["LU2147879543", "Tikehau International Cross Assets R Acc"],
    # ["LU1920211973", "Eleva Abs Return Europe Fd A2 EUR Acc"],
    ["LU0115098948", "JPMIF Global Macro Opport D (acc) EUR"],
    ["LU1582988058", "M&G Lux Dynamic Allocat Fd A EUR Acc"],
    ["LU2358389745", "Varenne Global A EUR"],
    ["LU1100076550", "Clartan Valeurs C EUR Acc"],
    ["FR0000284689", "Comgest Monde C"],
    ["FR0010321810", "Echiquier Agenor SRI Mid Cap Europe A"],
    ["FR0011153014", "Ginjer Actifs 360 A"],
    ["FR0010149302", "Carmignac Emergents A EUR Acc"],
    ["LU1261432659", "FF World Fund A Acc EUR"],
    ["LU0159053015", "JPM US Technology Fund D Acc EUR"],
    ["LU0386882277", "Pictet - Gbl Megatrend Select P EUR Acc"],
    ["FR0010187898", "R-co Conviction Equity Value Euro C EUR"],
    ["LU2257980289", "Mandarine Global Transition"],
    ["LU1183791794", "Sycomore Eco solution"],
    ["LU1956003765", "Mirova Women"],
    ["LU1301026388", "Sycomore Fund Happy"],
    ["FR0000970873", "Insertion Emplois Dynamique"],
    ["FR0010298596", "Moneta Multi Caps"],
    ["FR0010547869", "Sextant PME A"],
    ["FR0011363746", "Solidarite Habitat et Humanisme"],
    ["LU2257982228", "Mandarine Global Sport"],
    ["LU0880062913", "JPM Global Healthcare Fund"],
    ["LU1279334210", "Pictet Robotics"],
    ["LU1951225553", "NIF Lux Thematics Safety"],
    ["LU1819480192", "Echiquier Artificial Intelligence"]
]

def return_name():
    name = []
    for i in range(len(listeIsin)):
        name.append(listeIsin[i][1])
    return name

def return_isin(name):
    isin = ''
    for i in range(len(listeIsin)):
        if name == str(listeIsin[i][1]) : 
            isin = str(listeIsin[i][0])
            return isin

st.cache()
def load_isin_data(isin, _date=''):
    dataFunds = {}
    try:
        url = f'https://www.boursorama.com/recherche/{isin}?searchId='
        r = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        c = urlopen(r).read()
        soup = BeautifulSoup(c, "html.parser")
        newURL = "https://www.boursorama.com" + soup.find_all("a", {"class": "c-submenubar__link"})[2]['href']

        r = Request(newURL, headers={"User-Agent": "Mozilla/5.0"})
        c = urlopen(r).read()
        soup = BeautifulSoup(c, "html.parser")

        bloc_nom = soup.find('h1', 'c-faceplate__company-title')
        div_nom = bloc_nom.find('a')
        nom_fonds = div_nom.text.strip()
        
        bloc_valeur = soup.find('span', 'c-instrument c-instrument--last')
        valeur_fonds = bloc_valeur.text.strip()

        bloc_variation = soup.find('span', 'c-instrument c-instrument--variation')
        variation_fonds = bloc_variation.text.strip()

        risque_fonds = soup.find('div', 'c-gauge').get('data-gauge-current-step')

        noms = []
        prcts = []

        tbl_compo = soup.find('table', 'c-table c-table--bottom-space')

        for row in tbl_compo.find_all('tr'):
            columns = row.find_all('td')
            if columns != [] :
                nom_ligne = columns[0].text.strip()
                prct_ligne = columns[1].find('div').get('data-gauge-current-step')
                noms.append(nom_ligne)
                prcts.append(prct_ligne)

        if noms != [] and  prcts != [] : 
            ligne = pd.DataFrame({'Nom': noms, 'Pourcentage': prcts})
        else :
            ligne = np.nan

        m = re.findall('"amChartData":(\[.+])', str(soup))
        try:
            geographicalAlloc = pd.DataFrame(eval(m[0]))
        except:
            geographicalAlloc = np.nan

        try:
            typeAlloc = pd.DataFrame(eval(m[1]))
        except:
            typeAlloc = np.nan

        try:
            sectorAlloc = pd.DataFrame(eval(m[2]))
        except:
            sectorAlloc = np.nan
        
        dataFunds[isin] = [nom_fonds, valeur_fonds, variation_fonds, risque_fonds, ligne, geographicalAlloc, typeAlloc, sectorAlloc]

    except :
        dataFunds[isin] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
        
    return dataFunds


isin = "FR0010135103"

with st.sidebar:
    st.title("Dashboard Pôle Offre 💚")
    name_fonds = st.sidebar.selectbox(
     'Choisis un fonds',
     return_name()
    )

st.title(name_fonds)

isin_fonds = return_isin(name_fonds)

if st.sidebar.button('Check'):
    st.balloons()
    with st.spinner('Wait for it...'):
        alldata = pd.DataFrame(load_isin_data(isin_fonds, '')).transpose()
        alldata.columns = ['Fonds', 'Valeur', 'Variation', 'Risque', '10lignes', 'Geographie', 'Actifs', 'Secteurs']

        valeur_fonds = alldata.loc[isin_fonds,'Valeur']
        variation_fonds = alldata.loc[isin_fonds,'Variation']
        risque_fonds = alldata.loc[isin_fonds, 'Risque']

        placeholder = st.empty()
        with placeholder.container():
            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                label="CODE ISIN",
                value=isin_fonds
            )

            kpi2.metric(
                label="VALEUR",
                value=round(float(valeur_fonds),2),
                delta=f"{round(float(variation_fonds[:-1]),2)} %"
            )

            kpi3.metric(
                label="❗ RISQUE ❗",
                value=f"{int(risque_fonds)}/7"
            )

        dataFirst = pd.DataFrame()
        dataFirst = alldata.loc[isin_fonds, '10lignes']

        dataGeo = alldata.loc[isin_fonds, 'Geographie']

        dataActif = alldata.loc[isin_fonds, 'Actifs']

        dataSecteur = alldata.loc[isin_fonds, 'Secteurs']

        col1, col2 = st.columns(2)

        with col1 :
            st.markdown("### Allocation d'actifs")
            st.write(dataActif)

        with col2 :
            st.markdown("### Premières lignes")
            fig2 = alt.Chart(dataFirst).mark_bar().encode(
                x = 'Pourcentage:Q',
                y = alt.Y('Nom:N', sort='-x'),
                color = 'Pourcentage'
            )
            st.altair_chart(fig2, use_container_width=True)
            
        col3, col4 = st.columns(2)

        if isinstance(dataSecteur, float) == False :
            with col3 :
                st.markdown("### Secteurs")
                fig3, ax3 = plt.subplots()
                ax3.pie(dataSecteur['value'].values, labels=dataSecteur['name'].values, autopct='%1.1f%%', shadow=False, startangle=180)
                ax3.axis('equal')
                st.write(fig3)
        else :
            with col3 :
                st.write("Problème data !")

        with col4 :
            st.markdown("### Répartition géographique")
            fig4, ax4 = plt.subplots()
            ax4.pie(dataGeo['value'].values, labels=dataGeo['name'].values, autopct='%1.1f%%', shadow=False, startangle=180)
            ax4.axis('equal')
            st.write(fig4)