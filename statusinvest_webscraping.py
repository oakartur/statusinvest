#import libraries
import pandas as pd
from bs4 import BeautifulSoup
import requests
import sys
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import re
from itertools import islice

#CSV file with companies tickers
address = 'C:/Codes/Empresas B3/tickers.csv'
tickers = pd.read_csv(address)

#creates dictionaries
tickers_dict = {}
for ticker in tickers['TICKER']:
    ticker_df = tickers[tickers['TICKER'] == ticker]
    tickers_dict[ticker] = ticker_df
    
base_url = 'https://statusinvest.com.br/acoes/'

link_dict = {}
for ticker in tickers_dict.keys():
    link = base_url+ticker
    link_dict[ticker] = link

df_dict = {}
for ticker in tickers_dict.keys():
    df_dict[ticker] = []
    
soup_dict = {}

#access every link and gets the html - this should take about 80min 
for ticker, link in link_dict.items():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=400,800')
        browser = webdriver.Chrome(options=options)

        browser.get(link)
        sleep(2)
        
        # Encontre o botão "Histórico" e clique nele
        historico_button = browser.find_element(By.XPATH, '//button[@title="Histórico do ativo"]')
        historico_button.click()
        sleep(1)
        
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        # Utilize try/except para tratar a possibilidade de não encontrar as informações desejadas
        try:
            soup_dict[ticker] = soup.find_all('div', class_='tr w-100 d-flex justify-start asset-last')  
        except AttributeError:
            soup_dict[ticker] = []  # Retorne uma lista vazia se as informações não forem encontradas

    except Exception as e:
        print(f"Erro ao acessar o link para o ticker {ticker}: {e}")
        soup_dict[ticker] = []  # Retorne uma lista vazia em caso de erro

    finally:
        browser.quit()

#indicator list as shown on statusinvest        
indicadores = ['D.Y', 'P/L','PEG RATIO', 'P/VP', 'EV/EBITDA', 'EV/EBIT', 'P/EBITDA', 'P/EBIT',
               'VPA', 'P/ATIVO', 'LPA', 'P/SR', 'P/CAP. GIRO', 'P/ATIVO CIR. LIQ', 'DÍV. LIQ/PL',
               'DIV. LIQ/EBITDA', 'DIV. LIQ/EBIT', 'PL/ATIVOS', 'PASSIVOS/ATIVOS', 'LIQ. CORRENTE',
               'M.BRUTA', 'M.EBITDA', 'M.EBIT', 'M.LIQ', 'ROE', 'ROA', 'ROIC', 'GIRO ATIVOS', 'CAGR REC. 5',
               'CAGR LUCRO 5']

#default dictionary
default_dict = {
    'Indicadores': indicadores,
    'Atual': [0] * len(indicadores),
    '2022': [0] * len(indicadores),
    '2021': [0] * len(indicadores),
    '2020': [0] * len(indicadores),
    '2019': [0] * len(indicadores),
    '2018': [0] * len(indicadores),
    '2017': [0] * len(indicadores),
    '2016': [0] * len(indicadores),
    '2015': [0] * len(indicadores),
    '2014': [0] * len(indicadores),
}
#default df
default_df = pd.DataFrame(default_dict)

#gets indicators from soup
for ticker, soup in soup_dict.items():
    dado_atual = []
    dado_2022 = []
    dado_2021 = []
    dado_2020 = []
    dado_2019 = []
    dado_2018 = []
    dado_2017 = []
    dado_2016 = []
    dado_2015 = []
    dado_2014 = []

    for i in range(30):
        try:
            dado_atual.append(soup[i].contents[0].text)
        except IndexError:
            dado_atual.append(None)
        
        try:
            dado_2022.append(soup[i].contents[1].text)
        except IndexError:
            dado_2022.append(None)
        
        try:
            dado_2021.append(soup[i].contents[2].text)
        except IndexError:
            dado_2021.append(None)
        
        try:
            dado_2020.append(soup[i].contents[3].text)
        except IndexError:
            dado_2020.append(None)
        
        try:
            dado_2019.append(soup[i].contents[4].text)
        except IndexError:
            dado_2019.append(None)
        
        try:
            dado_2018.append(soup[i].contents[5].text)
        except IndexError:
            dado_2018.append(None)
        
        try:
            dado_2017.append(soup[i].contents[6].text)
        except IndexError:
            dado_2017.append(None)
        
        try:
            dado_2016.append(soup[i].contents[7].text)
        except IndexError:
            dado_2016.append(None)
        
        try:
            dado_2015.append(soup[i].contents[8].text)
        except IndexError:
            dado_2015.append(None)
        
        try:
            dado_2014.append(soup[i].contents[9].text)
        except IndexError:
            dado_2014.append(None)

    new_df = default_df.copy()
    new_df['Atual'] = dado_atual
    new_df['2022'] = dado_2022
    new_df['2021'] = dado_2021
    new_df['2020'] = dado_2020
    new_df['2019'] = dado_2019
    new_df['2018'] = dado_2018
    new_df['2017'] = dado_2017
    new_df['2016'] = dado_2016
    new_df['2015'] = dado_2015
    new_df['2014'] = dado_2014

    df_dict[ticker] = new_df
    
#converts to dfs
dfs = [pd.DataFrame(df) for df in df_dict.values()]

#Concatenate all DataFrames into a single DataFrame
all_dataframes = pd.concat(dfs, keys=df_dict.keys())

#saves into CSV
all_dataframes.to_csv('indicadores_b3.csv')