import pandas as pd
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime

# initializing chrome driver
chrome_service = Service(ChromeDriverManager().install())
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36")
chrome_options.add_argument("--headless")

dr = webdriver.Chrome(options=chrome_options, service=chrome_service)
WebDriverWait(dr, 10).until(lambda dr: dr.execute_script('return document.readyState') == 'complete')

# reading block numbers
dr.get('https://etherscan.io/blocks')
blocks_page = dr.page_source

soup = BeautifulSoup(blocks_page, 'html.parser')
table = soup.find('table')

tbody = table.find('tbody')
trs = tbody.find_all('tr')

block_numbers = []
for tr in trs[:10]:
    td = tr.find('td')
    block_number = td.text.strip()
    block_numbers.append(block_number)

print(f"{datetime.now().strftime("%H:%M:%S")}: getting last 10 block numbers done: \n\t{block_numbers}")

# reading transactions associated with the extracted block numbers
df = None
for block_number in block_numbers:
    print(f"{datetime.now().strftime("%H:%M:%S")}: getting all transactions associated with block number {block_number}")
    p = 1
    while True:
        url = f'https://etherscan.io/txs?block={block_number}&p={p}'
        sleep(0.5)

        dr.get(url)
        page = dr.page_source
        
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find('table')
        
        if df is None:
            thead = table.find('thead')
            thead_titles = thead.find_all('th')
            titles = [table_title.text.strip() for table_title in thead_titles]
            df = pd.DataFrame(columns=titles)
        
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        if len(trs) == 1: 
            break
        
        for tr in trs:
            tds = tr.find_all('td')
            tds = filter(lambda td: not (td.get('style') and 'display:none' in td.get('style')), tds)
            data = [td.text.strip() for td in tds]

            length = len(df)
            df.loc[length] = data
        p += 1
        
dr.quit()

print(f"{datetime.now().strftime("%H:%M:%S")}: saving data in 'data/data.csv'")
df.to_csv('data/data.csv', index=False)