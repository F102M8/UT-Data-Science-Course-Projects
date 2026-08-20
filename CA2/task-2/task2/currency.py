from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait


def find_exchange_rate(from_currency: str, to_currency: str = "USD") -> float:
    from_currency = from_currency.lower()
    to_currency = to_currency.lower()
    if from_currency == to_currency:
        return 1

    dr = _initialize_driver()
    url = f"https://www.google.com/search?q={from_currency}+to+{to_currency}"
    dr.get(url)
    search_page = dr.page_source
    soup = BeautifulSoup(search_page, 'html.parser')
    try:
        usd_equivalent = _extract_exchange_rate_from_soup(soup)
    except Exception as e:
        raise Exception(f"{from_currency} -> {to_currency} : {e}")

    dr.quit()
    return usd_equivalent


def _initialize_driver() -> webdriver.Chrome:
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/88.0.4324.150 Safari/537.36")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    dr = webdriver.Chrome(options=chrome_options, service=chrome_service)
    WebDriverWait(dr, 10).until(lambda _dr: _dr.execute_script('return document.readyState') == 'complete')
    return dr


def _extract_exchange_rate_from_soup(soup: BeautifulSoup) -> float:
    span = soup.find(class_='SwHCTb')
    if span is None:
        span = soup.find(class_='curr_totxt')
    if span is None:
        raise Exception('No exchange rate found by google search')
    return float(span.text.replace(',', ''))


if __name__ == "__main__":
    test = find_exchange_rate(from_currency='Saudi Arabian Rials', to_currency="Iranian Rials")
    print(test)
