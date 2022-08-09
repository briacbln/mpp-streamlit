from cProfile import label
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import streamlit as st
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import altair as alt


st.set_page_config(
    page_title = "Offre MPP - Description",
    page_icon = "📊",
    layout = "wide"
)

listePf = [
    ["Volontaire", "5", "3", "3%"],
    ["Énergique", "5", "4", "5%"],
    ["Ambitieux", "6", "5", "8%", ],
    ["Intrépide", "6", "6", "12%", ],
    ["Climat", "5", "5", "-",],
    ["Tech", "3", "6", "-", ],
    ["Relance", "3", "6", "-", ],
    ["Santé", "2", "6", "-", ],
    ["Solidarité", "1", "3", "-", ],
    ["Égalité", "1", "6", "-", ],
    ["Emploi", "2", "5", "-", ],
]

listePortefeuilles = {
    "Volontaire" : {
        "FR0010135103" : 0.25,
        "LU1694789535" : 0.2,
        "FR0010687053" : 0.15,
        "FR0012355139" : 0.25,
        "LU2147879543" : 0.15
    },
    "Énergique" : {
        # "LU1920211973" : 0.2,
        "LU0115098948" : 0.25,
        "FR0012355139" : 0.2,
        "LU1582988058" : 0.15,
        "LU2358389745" : 0.2
    },
    "Ambitieux" : {
        "LU1100076550" : 0.18,
        "FR0000284689" : 0.17,
        "FR0010321810" : 0.11,
        "FR0011153014" : 0.18,
        "LU1582988058" : 0.15,
        "LU2358389745" : 0.21
    },
    "Intrépide" : {
        "FR0010149302" : 0.2,
        "FR0000284689" : 0.19,
        "LU1261432659" : 0.17,
        "LU0159053015" : 0.11,
        "LU0386882277" : 0.13,
        "FR0010187898" : 0.2
    },
    "Climat" : {
        "LU2257980289" : 0.22,
        "LU1183791794" : 0.23,
        "LU0914733059" : 0.20,
        "FR0010642280" : 0.20,
        "FR0013411741" : 0.15
    },
    "Tech" : {
        "LU1819480192" : 0.34,
        "LU1279334210" : 0.33,
        "LU1951225553" : 0.33
    },
    "Relance" : {
        "FR0010298596" : 0.33,
        "FR0000970873" : 0.34,
        "FR0010547869" : 0.33
    },
    "Santé" : {
        "LU2257982228" : 0.5,
        "LU0880062913" : 0.5
    },
    "Solidarité" : {
        "FR0011363746" : 1
    },
    "Égalité" : {
        "LU1956003765" : 1
    },
    "Emploi" : {
        "LU1301026388" : 0.5,
        "FR0000970873" : 0.5
    }
}

listeIsin = [
    ["FR0010135103", "Carmignac Patrimoine A EUR Acc", "", "Croissance", "Grande"],
    ["LU1694789535", "DNCA Invest Alpha Bonds B EUR Acc", "", "", ""],
    ["FR0010687053", "Dorval Global Convictions R", "ISR", "Mixte", "Grande"],
    ["FR0012355139", "Lazard Patrimoine SRI RC EUR", "ISR", "Mixte", "Grande"],
    ["LU2147879543", "Tikehau International Cross Assets R Acc", "", "Croissance", "Grande"],
    # ["LU1920211973", "Eleva Abs Return Europe Fd A2 EUR Acc", ""],
    ["LU0115098948", "JPMIF Global Macro Opport D (acc) EUR", "", "Croissance", "Grande"],
    ["LU1582988058", "M&G Lux Dynamic Allocat Fd A EUR Acc", "", "Valeur", "Grande"],
    ["LU2358389745", "Varenne Global A EUR", "", "Mixte", "Grande"],
    ["LU1100076550", "Clartan Valeurs C EUR Acc", "", "Valeur", "Grande"],
    ["FR0000284689", "Comgest Monde C", "", "Croissance", "Grande"],
    ["FR0010321810", "Echiquier Agenor SRI Mid Cap Europe A", "ISR", "Croissance", "Mid"],
    ["FR0011153014", "Ginjer Actifs 360 A", "", "Valeur", "Grande"],
    ["FR0010149302", "Carmignac Emergents A EUR Acc", "ISR", "Mixte", "Grande"],
    ["LU1261432659", "FF World Fund A Acc EUR", "", "Mixte", "Grande"],
    ["LU0159053015", "JPM US Technology Fund D Acc EUR", "", "Croissance", "Grande"],
    ["LU0386882277", "Pictet - Gbl Megatrend Select P EUR Acc", "", "Croissance", "Grande"],
    ["FR0010187898", "R-co Conviction Equity Value Euro C EUR", "", "Valeur", "Grande"],
    ["LU2257980289", "Mandarine Global Transition", "GREENFIN", "Croissance", "Grande"],
    ["LU1183791794", "Sycomore Eco solution", "ISR - GREENFIN", "Croissance", "Moyenne"],
    ["LU1956003765", "Mirova Women", "ISR", "Croissance", "Grande"],
    ["LU1301026388", "Sycomore Fund Happy", "ISR", "Croissance", "Grande"],
    ["FR0000970873", "Insertion Emplois Dynamique", "ISR - FINANSOL - RELANCE", "Croissance", "Grande"],
    ["FR0010298596", "Moneta Multi Caps", "RELANCE", "Mixte", "Moyenne"],
    ["FR0010547869", "Sextant PME A", "ISR - RELANCE", "Mixte", "Petite"],
    ["FR0011363746", "Solidarite Habitat et Humanisme", "FINANSOL", "Mixte", "Grande"],
    ["LU2257982228", "Mandarine Global Sport", "ISR", "Croissance", "Moyenne"],
    ["LU0880062913", "JPM Global Healthcare Fund", "", "Croissance", "Grande"],
    ["LU1279334210", "Pictet Robotics", "", "Croissance", "Grande"],
    ["LU1951225553", "NIF Lux Thematics Safety", "ISR", "Croissance", "Moyenne"],
    ["LU1819480192", "Echiquier Artificial Intelligence", "", "Croissance", "Grande"],
    ["LU0914733059", "Mirova Europe Environmental Eq R EUR Acc", "ISR - GREENFIN", "Croissance", "Grande"],
    ["FR0010642280", "Ecofi Agir Pour Le Climat C", "ISR - GREENFIN - FINANSOL", "Croissance", "Grande"],
    ["FR0013411741", "Amundi RI Impact Green Bonds P Acc", "GREENFIN", "Croissance", "Grande"]
]

# Fonctions pour récupérer données portefeuille
@st.cache()
def return_pf_nbfonds(nom_portefeuille):
    nbfonds = 0
    # for i in range(len(listePf)):
    #     if nom_portefeuille == str(listePf[i][0]) :
    #         nbfonds = listePf[i][1]
    # return nbfonds
    for key, value in listePortefeuilles.items() :
        if nom_portefeuille == key :
            for i in value.items():
                nbfonds += 1
    return nbfonds

@st.cache()
def return_pf_risque(nom_portefeuille):
    risque = 0
    for i in range(len(listePf)):
        if nom_portefeuille == str(listePf[i][0]) :
            risque = listePf[i][2]
    return risque

@st.cache()
def return_pf_perf(nom_portefeuille):
    perf = 0
    for i in range(len(listePf)):
        if nom_portefeuille == str(listePf[i][0]) :
            perf = listePf[i][3]
    return perf

@st.cache()
def return_noms_pf(nom_portefeuille):
    noms = []
    isin = listePortefeuilles[nom_portefeuille]
    # print(isin)
    for i in range(len(listeIsin)):
        for cle in isin :
            if listeIsin[i][0] == cle :
                noms.append(listeIsin[i][1])
    return noms

# Fonction qui retourne la liste des portefeuilles
def return_portefeuilles():
    portefeuilles = []
    for cle in listePortefeuilles :
        portefeuilles.append(cle)
    return portefeuilles

@st.cache()
def return_data_fonds(nom, nb):
    data = ""
    for i in range(len(listeIsin)):
        if nom == str(listeIsin[i][1]) : 
            data = str(listeIsin[i][nb])
            if data == "" :
                return "-"
            else :
                return data

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

        # print("nom : " + nom_fonds, ", valeur : " + valeur_fonds, ", variation : ", variation_fonds, ", risque : ", risque_fonds)

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

def clean_value(value):
    if str(" ") in value :
        return round(float(value.replace(" ", "")),2)
    else :
        return round(float(value),2)

with st.sidebar :
    nom_portefeuille = st.sidebar.selectbox(
        "Choisis un portefeuille",
        return_portefeuilles()
    )
    nom_fonds = st.sidebar.selectbox(
        "Choisis un fonds puis appuie sur le bouton",
        return_noms_pf(nom_portefeuille)
    )

st.title(nom_portefeuille)

isin_fonds = return_data_fonds(nom_fonds, 0)
label_fonds = return_data_fonds(nom_fonds, 2)
action_fonds = return_data_fonds(nom_fonds, 3)
cap_fonds = return_data_fonds(nom_fonds, 4)

if st.sidebar.button("Rechercher") :

    st.balloons()

    st.write("### " + nom_fonds)

    with st.spinner("En cours de chargement...") :
        alldata = pd.DataFrame(load_isin_data(isin_fonds, '').copy()).transpose().copy()
        alldata.columns = ['Fonds', 'Valeur', 'Variation', 'Risque', '10lignes', 'Geographie', 'Actifs', 'Secteurs']

        valeur_fonds = alldata.copy().loc[isin_fonds,'Valeur']
        variation_fonds = alldata.copy().loc[isin_fonds,'Variation']
        risque_fonds = alldata.copy().loc[isin_fonds, 'Risque']

        placeholder = st.empty()
        with placeholder.container():
            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                label = "ISIN",
                value = isin_fonds
            )

            kpi2.metric(
                label = "Valeur",
                value = clean_value(valeur_fonds),
                delta = f"{round(float(variation_fonds[:-1]),2)} %"
            )

            kpi3.metric(
                label = "Risque",
                value = f"{int(risque_fonds)}/7"
            )
        
        placeholder2 = st.empty()
        with placeholder2.container():
            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                label = "Label",
                value = label_fonds
            )

            kpi2.metric(
                label = "Action",
                value = action_fonds
            )

            kpi3.metric(
                label = "Capitalisation",
                value = cap_fonds
            )

        dataActif = alldata.copy().loc[isin_fonds, 'Actifs']
        dataActif.columns = ['Actifs', 'Pourcentage']
        dataActif['Pourcentage'] = dataActif['Pourcentage'].div(dataActif['Pourcentage'].sum()).multiply(100)

        dataFirst = alldata.copy().loc[isin_fonds, '10lignes']

        dataSecteur = alldata.copy().loc[isin_fonds, 'Secteurs']

        dataGeo = alldata.copy().loc[isin_fonds, 'Geographie']

        col1, col2 = st.columns(2)
        
        if isinstance(dataActif, float) == False :
            with col1 :
                st.markdown("### Allocation d'actifs")
                st.write(dataActif)

        else :
            with col1 :
                st.write("### ❌ Pas de données sur l'allocation d'actifs")

        if isinstance(dataFirst, float) == False :
            with col2 :
                st.markdown("### 10 premières lignes")
                fig2 = alt.Chart(dataFirst).mark_bar().encode(
                    x = 'Pourcentage:Q',
                    y = alt.Y('Nom:N', sort='-x'),
                    color = 'Pourcentage'
                )
                st.altair_chart(fig2, use_container_width=True)
        else :
            with col2 :
                st.write("### ❌ Pas de données sur les 10 premières lignes")
            
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
                st.write("### ❌ Pas de données sur les secteurs")

        if isinstance(dataGeo, float) == False :
            with col4 :
                st.markdown("### Répartition géographique")
                fig4, ax4 = plt.subplots()
                ax4.pie(dataGeo['value'].values, labels=dataGeo['name'].values, autopct='%1.1f%%', shadow=False, startangle=180)
                ax4.axis('equal')
                st.write(fig4)
        else :
            with col4 :
                st.write("### ❌ Pas de données sur l'exposition géographique")

else :
    nbfonds_portefeuille = return_pf_nbfonds(nom_portefeuille)
    risque_portefeuille = return_pf_risque(nom_portefeuille)
    perf_portefeuille = return_pf_perf(nom_portefeuille)
    
    with st.spinner("En cours de chargement...") :
        liste_isins_fonds = listePortefeuilles[nom_portefeuille]

        alldata_pf = pd.DataFrame()
        ponde = []
        liste = []
        for isin_fonds in liste_isins_fonds :
            # print("isin : ", isin_fonds)
            # print("val : ", liste_isins_fonds.get(isin_fonds))
            ponde.append(liste_isins_fonds.get(isin_fonds))
            liste.append(pd.DataFrame(load_isin_data(isin_fonds, '').copy()).transpose().copy())

        alldata_pf = pd.concat(liste, ignore_index=True)
        alldata_pf = alldata_pf.reset_index(drop=True)
        alldata_pf.columns = ['Fonds', 'Valeur', 'Variation', 'Risque', '10lignes', 'Geographie', 'Actifs', 'Secteurs']
        alldata_pf['Ponderation'] = ponde

        fonds_pf = alldata_pf[['Fonds', 'Ponderation', 'Valeur', 'Variation', 'Risque']]
        fonds_pf['Ponderation'] = round(100*fonds_pf['Ponderation'], 0)
        fonds_pf['Ponderation'] = fonds_pf['Ponderation'].astype(str) + "%"

        placeholder = st.empty()
        with placeholder.container() :
            kpi1, kpi2, kpi3 = st.columns(3)

            kpi1.metric(
                label = "Nombre de fonds",
                value = nbfonds_portefeuille
            )

            kpi2.metric(
                label = "Risque",
                value = risque_portefeuille
            )

            kpi3.metric(
                label = "Objectif de performance",
                value = perf_portefeuille
            )
        
        # st.write("### Liste des fonds")
        # st.write(fonds_pf)

        dataActif_pf = pd.DataFrame()
        listeActif_pf = []
        for i in alldata_pf.index : 
            dataActif_i = pd.DataFrame()
            dataActif_i = alldata_pf.copy().loc[i, 'Actifs']
            try:
                dataActif_i['value'] = dataActif_i['value'].multiply(ponde[i])
            except:
                continue
            if isinstance(alldata_pf.copy().loc[i, 'Actifs'], float) == False : 
                listeActif_pf.append(dataActif_i)
        dataActif_pf = pd.concat(listeActif_pf, ignore_index=True)
        dataActif_pf = dataActif_pf.groupby(['name'])['value'].sum()
        dataActif_pf = dataActif_pf.to_frame()
        dataActif_pf.reset_index(inplace=True)
        dataActif_pf.columns = ['Actifs', 'Pourcentage']
        dataActif_pf['Pourcentage'] = dataActif_pf['Pourcentage'].div(dataActif_pf['Pourcentage'].sum()).multiply(100)
        
        dataSecteur_pf = pd.DataFrame()
        listeSecteur_pf = []
        for i in alldata_pf.index : 
            dataSecteur_i = pd.DataFrame()
            dataSecteur_i = alldata_pf.copy().loc[i, 'Secteurs']
            try:
                dataSecteur_i['value'] = dataSecteur_i['value'].multiply(ponde[i])
            except:
                continue
            if isinstance(dataSecteur_i, float) == False :
                listeSecteur_pf.append(dataSecteur_i)
    
        dataSecteur_pf = pd.concat(listeSecteur_pf, ignore_index=True)
        dataSecteur_pf = dataSecteur_pf.groupby(['name'])['value'].sum()
        dataSecteur_pf.columns = ['Secteur', 'Pourcentage']

        dataGeo_pf = pd.DataFrame()
        listeGeo_pf = []
        for i in alldata_pf.index : 
            dataGeo_i = pd.DataFrame()
            dataGeo_i = alldata_pf.copy().loc[i,'Geographie']
            try:
                dataGeo_i['value'] = dataGeo_i['value'].multiply(ponde[i])
            except:
                continue
            if isinstance(dataGeo_i, float) == False :            
                listeGeo_pf.append(dataGeo_i)

        dataGeo_pf = pd.concat(listeGeo_pf, ignore_index=True)
        dataGeo_pf = dataGeo_pf.groupby(['name'])['value'].sum()
        dataGeo_pf = dataGeo_pf.to_frame()
        dataGeo_pf.reset_index(inplace=True)
        dataGeo_pf.columns = ['Pays', 'Pourcentage']

        col1, col2 = st.columns(2)

        with col1 :
            st.write("### Liste des fonds")
            st.write(fonds_pf)
        
        with col2 :
            st.markdown("### Allocation d'actifs")
            st.write(dataActif_pf)
        
        col3, col4 = st.columns(2)

        if len(dataSecteur_pf.columns) == 0 :
            with col3 :
                st.write("### ❌ Pas de données sur les secteurs")
        else : 
            with col3 :
                st.markdown("### Secteurs")
                fig1, ax1 = plt.subplots()
                ax1.pie(dataSecteur_pf.values, labels=dataSecteur_pf.index, autopct='%1.1f%%', shadow=False, startangle=180)
                ax1.axis('equal')
                st.write(fig1)

        if len(dataGeo_pf.columns) == 0 : 
            with col4 :
                st.write("### ❌ Pas de données sur l'exposition géographique'")
        else : 
            with col4 :
                st.markdown("### Répartition géographique")
                fig2 = alt.Chart(dataGeo_pf).mark_bar().encode(
                    x = 'Pourcentage',
                    y = alt.Y('Pays', sort='-x'),
                    color = 'Pourcentage'
                )
                st.altair_chart(fig2, use_container_width=True)
