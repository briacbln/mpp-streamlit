import streamlit as st
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import time

st.set_page_config(
    page_title = "Offre MPP - Performance",
    page_icon = "📈",
    layout = "wide"
)

# Id des fonds (dans l'URL) sur Morningstar
ids_fonds = [
    "F0GBR04F90", # Volontaire : Carmignac Patrimoine A EUR Acc
    "F00000ZY7M", # Volontaire : DNCA Invest Alpha Bonds B EUR Acc
    "F000003Y4O", # Volontaire : Dorval Global Convictions R
    "F00000V7MO", # Volontaire : Lazard Patrimoine SRI RC EUR
    "F0000165CN", # Volontaire : Tikehau International Cross Assets R Acc
    "F000013DD9", # Énergique : Eleva Abs Return Europe Fd A2 EUR Acc
    "F0GBR04N04", # Énergique : JPMIF Global Macro Opport D (acc) EUR
    "F00000V7MO", # Énergique : Lazard Patrimoine SRI RC EUR
    "F00000ZY64", # Énergique : M&G Lux Dynamic Allocat Fd A EUR Acc
    "F00001DGJL", # Énergique : Varenne Global A EUR
    "F00000V7KE", # Ambitieux : Clartan Valeurs C EUR Acc
    "F0GBR04QCM", # Ambitieux : Comgest Monde C
    "F0GBR04VT4", # Ambitieux : Echiquier Agenor SRI Mid Cap Europe A
    "F00000NGS6", # Ambitieux : Ginjer Actifs 360 A
    "F00000ZY64", # Ambitieux : M&G Lux Dynamic Allocat Fd A EUR Acc
    "F00001DGJL", # Ambitieux : Varenne Global A EUR
    "F0GBR04F8J", # Intrépide : Carmignac Emergents A EUR Acc
    "F0GBR04QCM", # Intrépide : Comgest Monde C
    "F00000W422", # Intrépide : FF World Fund A Acc EUR
    "F000005MPD", # Intrépide : JPM US Technology Fund D Acc EUR
    "F0000026WJ", # Intrépide : Pictet - Gbl Megatrend Select P EUR Acc
    "F0GBR05YT7", # Intrépide : R-co Conviction Equity Value Euro C EUR
    "F000016OYU", # Climat : Mandarine Global Transition
    "F00000WDKJ", # Climat : Sycomore Eco solution
    "F000013HWO", # Égalité : Mirova Women
    "F0GBR04GGX", # Emploi : Insertion Emplois Dynamique
    "F00000WI8D", # Emploi : Sycomoree Fund Happy
    "F0GBR04GGX", # Relance : Insertion Emplois Dynamique
    "F0GBR06TFP", # Relance : Moneta Multi Caps
    "F000000OZU", # Relance : Sextant PME A
    "F00000POB7", # Solidarité :  Solidarite Habitat et Humanisme
    "F000016GM5", # Santé : Mandarine Global Sport
    "F00000PIIR", # Santé : JPM Global Healthcare Fund
    "F00000WFC3", # Tech : Pictet Robotics
    "F000013BMI", # Tech : NIF Lux Thematics Safety
    "F000010S65" # Tech : Echiquier Artificial Intelligence"""
]

# Crée de l'url avec l'id du fonds
def build_url_fond(_id):
    return "https://www.morningstar.fr/fr/funds/snapshot/snapshot.aspx?tab=1&id=" + str(_id)

# Remplace la virgule par un point
def Replace(string): 
    maketrans = string.maketrans 
    final = string.translate(maketrans(',', '.')) 
    return final

@st.cache()
def recup_fonds(ids):
    frames = []
    for _id in ids:
        time.sleep(0.5)
        # Créer l'URL pour le fonds
        url = build_url_fond(_id)

        s_perf = []

        # Charge la page Morningstar du fonds
        soup = BeautifulSoup(requests.get(url).content, "html.parser")

        if soup is None:
            # print('Could not load soup ', _id)
            continue

        # Cherche le nom du fonds
        fonds = soup.find('div', id='snapshotTitleDiv')
        #print(fonds)
        #nom = fonds.find('h1')
        if fonds is None:
            # print('Could not load fonds ', _id)
            continue
        nom_fonds = fonds.find('h1').text.strip()
        # print(nom_fonds)

        # Trouve le bon tableau
        tbl = soup.find('div', id="returnsTrailingDiv")    

        # Enlève les 2 premières lignes inutiles du tableau
        tbl.tr.extract()
        tbl.tr.extract()

        # Parcourt toutes les 10 premières lignes du tableau Perf glissante de Morningstar
        for row in tbl.find_all('tr')[:10]:
            
            # Find all data for each column
            columns = row.find_all('td')

            # Parcourt toutes les colonnes et on récupère uniquement la perf    
            if (columns != [] and len(columns) == 4) :
                perf = Replace(columns[1].text.strip())
                # print(perf)
                # Après avoir remplacé la virgule par le point, on converti en float 
                if perf != "-" :
                    perf = round(float(perf), 2)
                elif perf == "-" :
                    perf = 0
                # Ajout des perf pour chaque période à notre tableau de perf
                s_perf.append(perf)

        # Création du dataframe propre au fonds
        df_par_fond = pd.DataFrame({nom_fonds : s_perf}, index=['1 jour', '1 semaine', '1 mois', '3 mois', '6 mois', 'YTD', '1 an', '3 ans annualisé', '5 ans annualisé', '10 ans annualisé'])
        
        # Ajout du dataframe du fonds aux tableaux de dataframes
        frames.append(df_par_fond)
    return frames

def precision_value(df):
    return df.round(2)#.style.format(precision=2)

# Création d'un seul dataframe pour tous les portefeuilles
df = pd.concat(recup_fonds(ids_fonds), axis=1)

# Volontaire
volontaire = [0 for i in range(6)]
volontaire_ponde = [0.25, 0.2, 0.15, 0.25, 0.15]
for i in range(0,6) :
    for j in range (0,5) :
        volontaire[i] += round(df.iloc[i, j] * volontaire_ponde[j], 2)
df_volontaire = precision_value(df.iloc[:,0:5].T.copy())

# Énergique
energique = [0 for i in range(6)]
energique_ponde = [0.2, 0.25, 0.2, 0.15, 0.2]
for i in range(0,6) :
    for j in range (0,5) :
        energique[i] += round(df.iloc[i, 5+j] * energique_ponde[j], 2)
df_energique = precision_value(df.iloc[:,5:10].T.copy())

# Ambitieux
ambitieux = [0 for i in range(6)]
ambitieux_ponde = [0.18, 0.17, 0.11, 0.18, 0.15, 0.21]
for i in range(0,6) :
    for j in range (0,6) :
        ambitieux[i] += round(df.iloc[i, 10+j] * ambitieux_ponde[j], 2)
df_ambitieux = precision_value(df.iloc[:,10:16].T.copy())

# Intrépide
intrepide = [0 for i in range(6)]
intrepide_ponde = [0.2, 0.19, 0.17, 0.11, 0.13, 0.2]
for i in range(0,6) :
    for j in range (0,6) :
        intrepide[i] += round(df.iloc[i, 16+j] * intrepide_ponde[j], 2)
df_intrepide = precision_value(df.iloc[:,16:22].T.copy())

# Climat 
climat = [0 for i in range(6)]
climat_ponde = [0.5, 0.5]
for i in range(0,6) :
    for j in range (0,2) :
        climat[i] += round(df.iloc[i, 22+j] * climat_ponde[j], 2)
df_climat = precision_value(df.iloc[:,22:24].T.copy())

# Égalité 
egalite = [0 for i in range(6)]
egalite_ponde = 1
for i in range(0,6) :
    egalite[i] += round(df.iloc[i, 24] * egalite_ponde, 2)
df_egalite = precision_value(df.iloc[:,24:25].T.copy())

# Emploi 
emploi = [0 for i in range(6)]
emploi_ponde = [0.5, 0.5]
for i in range(0,6) :
    for j in range (0,2) :
        emploi[i] += round(df.iloc[i, 22+j] * emploi_ponde[j], 2)
df_emploi = precision_value(df.iloc[:,25:27].T.copy())

# Relance 
relance = [0 for i in range(6)]
relance_ponde = [0.33, 0.34, 0.33]
for i in range(0,6) :
    for j in range (0,3) :
        relance[i] += round(df.iloc[i, 22+j] * relance_ponde[j], 2)
df_relance = precision_value(df.iloc[:,27:30].T.copy())

# Solidarité 
solidarite = [0 for i in range(6)]
solidarite_ponde = 1
for i in range(0,6) :
    solidarite[i] += round(df.iloc[i, 24] * solidarite_ponde, 2)
df_solidarite = precision_value(df.iloc[:,30:31].T.copy())

# Santé 
sante = [0 for i in range(6)]
sante_ponde = [0.5, 0.5]
for i in range(0,6) :
    for j in range (0,2) :
        sante[i] += round(df.iloc[i, 22+j] * sante_ponde[j], 2)
df_sante = precision_value(df.iloc[:,31:33].T.copy())

# Tech 
tech = [0 for i in range(6)]
tech_ponde = [0.34, 0.33, 0.33]
for i in range(0,6) :
    for j in range (0,3) :
        tech[i] += round(df.iloc[i, 22+j] * tech_ponde[j], 2)
df_tech = precision_value(df.iloc[:,33:36].T.copy())

perf_portefeuilles = np.zeros((6,11))
for i in range(0, 6) :
    perf_portefeuilles[i] = [volontaire[i], energique[i], ambitieux[i], intrepide[i], 
        climat[i], egalite[i], emploi[i], relance[i], solidarite[i], sante[i], tech[i]]

row_indices = ['1 jour', '1 semaine', '1 mois', '3 mois ', '6 mois', 'YTD']
column_indices = ['Volontaire', 'Énergique', 'Ambitieux', 'Intrépide', 
    'Climat', 'Égalité', 'Emploi', 'Relance', 'Solidarité', 'Santé', 'Tech']

df_perf = pd.DataFrame(perf_portefeuilles, index = row_indices, columns = column_indices)
df_perf = precision_value(df_perf.T)

st.write("### 📈 Performances ")

tab1, tab2 = st.tabs(["Portefeuilles", "Fonds"])

with tab1 :
    st.write("## Performances des portefeuilles")
    st.write(df_perf)

with tab2 : 
    st.write("## Performances des fonds détaillées")

    st.write("## Volontaire")
    st.write(df_volontaire)

    st.write("## Énergique")
    st.write(df_energique)

    st.write("## Ambitieux")
    st.write(df_ambitieux)

    st.write("## Intrépide")
    st.write(df_intrepide)

    st.write("## Climat")
    st.write(df_climat)

    st.write("## Égalité")
    st.write(df_egalite)

    st.write("## Emploi")
    st.write(df_emploi)

    st.write("## Relance")
    st.write(df_relance)

    st.write("## Solidarité")
    st.write(df_solidarite)

    st.write("## Santé")
    st.write(df_sante)

    st.write("## Tech")
    st.write(df_tech)