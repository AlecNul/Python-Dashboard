import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime 
import time
import os

def scrape_news():
    # Scraping
    url = "https://finviz.com/news.ashx?v=3"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'} # To bypass the Just a moment, cookies window
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Parsing
    links = []
    titles = []
    tickers = []
    data = []

    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for e in soup.find_all('tr', class_='news_table-row'):

        # Links
        subsoup_links = e.find('a', class_='nn-tab-link')
        link = subsoup_links.get('href')
        if (link[0] == '/'): # Sometimes the links begin with '/' bc the news website is finviz
            link = f"https://finviz.com{link}"
        links.append(link)

        # Titles
        subsoup_titles = e.find('a', class_='nn-tab-link')
        title = subsoup_titles.get_text()
        titles.append(title)

        # Tickers
        subsoup_tickers = e.find_all('a', class_='stock-news-label')
        tickers_list = []
        for ticker_class in subsoup_tickers:
            ticker_text = ticker_class.get('href')
            ticker = ticker_text.split('=')[1]
            tickers_list.append(ticker)
        tickers.append(tickers_list)

        row = {
                'date': scan_time,
                'tickers': tickers_list,
                'title': title,
                'link': link
            }
        data.append(row)
    
    # Put data to csv
    df = pd.DataFrame(data)
    filepath = 'src/data/news_data.csv'
    header_mode = not os.path.exists(filepath) # So we make only one header
    df.to_csv(filepath, mode='a', index=False, header=header_mode)

def get_latest_news(n=5):
    """
    Returns the news scraped on Finviz
    """
    file_path = 'src/data/news_data.csv'

    if not os.path.exists(file_path):
        return pd.DataFrame() 
    else:
        df = pd.read_csv(file_path)
        df = df.iloc[::-1] # get the latest news first
        return df.head(n)

# In order to launch it on cmd, will use KeyboardInterrupt to stop it
# python src/load_data/news_scraper.py
if __name__ == "__main__":
    print("Scraper launched, Ctrl+C to stop")
    try:
        while True:
            scrape_news()
            print(f"Next time at : {datetime.now().hour + 1}h)")
            time.sleep(3600)

    except KeyboardInterrupt:
        print("Scraper stopped (KeyboardInterrupt)")