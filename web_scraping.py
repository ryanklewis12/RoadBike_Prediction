import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd

def scrape_data():
    urls = [
        'https://www.amazon.com/Tommaso-Forcella-Endurance-Aluminum-Shimano/dp/B01NBHRM8K/ref=sr_1_2_sspa?crid=35W8CHG6Y4RH8&dib=eyJ2IjoiMSJ9.fZKqW08GvfQF2Mk3t6QcJOHvmROzSyT7PnGkxPDrEhLGjHj071QN20LucGBJIEps.uZ4xyB1hSx_2rMOuP81YqTyrP4KKA2DcyO1vdE-2GHc&dib_tag=se&keywords=Tommaso%2BForcella&qid=1723601147&sprefix=tommaso%2Bforcella%2Caps%2C166&sr=8-2-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&th=1&psc=1',
        'https://www.amazon.com/Schwinn-Featuring-Aluminum-Step-Over-Drivetrain/dp/B0183SF2XU/ref=sr_1_1?dib=eyJ2IjoiMSJ9.B4B31FPQTY7OwDoJJAq4s2LXp-Zh1fyFrOzzK59EjxRWR0GDqhpEyQ4Q_RxdZZDtzUCZV1RdR0o_XvYkuSf8j0U0qSHyPR2cvQFl3ioXrkc.qTKLQpvVVej1hTEge0YhNpvZr1a1PD2v3pP8CDge1CY&dib_tag=se&keywords=Schwinn%2BPhocus%2B1600&qid=1724029816&s=sporting-goods&sr=1-1&th=1',
        'https://www.amazon.com/Tommaso-Endurance-Aluminum-Shimano-Claris/dp/B01ACEYM8Y/ref=sr_1_1_sspa?adgrpid=1346902307311071&dib=eyJ2IjoiMSJ9.1f1c9fXI7lAV-7PTATiIGayb7CRItiX1EFidlBa71PDGjHj071QN20LucGBJIEps.Q4LIxQLrIMbUGOO352TXDzhFEhWxHzC_rkrmBS4qPlw&dib_tag=se&hvadid=84181465061976&hvbmt=be&hvdev=c&hvlocint=1826&hvlocphy=114010&hvnetw=o&hvqmt=e&hvtargid=kwd-84181734728374%3Aloc-190&hydadcr=2394_10653508&keywords=tommaso+imola&msclkid=835878bc0a321e551d111e7e96b9b0f7&qid=1724030101&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1',
        'https://www.amazon.com/Schwinn-Volare-Fitness-Bicycle-Medium/dp/B01N5XTB94/ref=sr_1_1?crid=37XRKOSGLNUOD&dib=eyJ2IjoiMSJ9.0mOhULBpRiMYeJ5s-T1SEG4fG_d1UyNHU2d0Z0jabdK84kfkUFbwLMN-MUD0dr6tw6SmC5OsjBFrjGfV50CYyUcz75KSc5pLZ65q-RbPa1ojE9xYVAhohxA_ybfzdXQ6kXxDlRUSiiBCuUMe2pGr__JI82IUUiTyMFbD5MChzFihOq4UbTmV2KSdbncDAEBlCJrOfy0m2zdqAGn52ylddXzkHXN0Ericjl9DQHSB0OWMcPmGOt9ixERziyEnmJ1KnTfPzhGLSwTATkv0XSSNRufpyuhDrKj3ouZeI_lLs3k.eTxjpQhty3vVUtA93HSrzURQoQwcArFq_3qoBMx1gSw&dib_tag=se&keywords=Schwinn+Volare+1400&qid=1724030639&s=sporting-goods&sprefix=schwinn+volare+1400%2Csporting%2C145&sr=1-1'
    ]

    bike_exchange_review = ['https://bikexchange.com/tommaso-forcella-review/', 'https://bikexchange.com/tommaso-imola-review/']
    bikes_insider_review = ['https://bikesinsider.com/road-bikes/schwinn-volare-review/']
    pedal_chef_review = ['https://www.pedalchef.com/post/schwinn-phocus-1600-reviews']

    chrome_driver_path = './chromedriver.exe'

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(executable_path=chrome_driver_path)

    def get_data_from_urls(urls, data_key, parse_func):
        driver = webdriver.Chrome(service=service, options=chrome_options)
        products_data = []

        for url in urls:
            driver.get(url)
            time.sleep(20)  # Allow some time for the page to load completely

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_data = parse_func(soup)
            products_data.append(product_data)

        driver.quit()
        return pd.DataFrame(products_data)

    def amazon_parse_func(soup):
        product_data = {}
        product_data['title'] = soup.find(id='productTitle').get_text(strip=True) if soup.find(id='productTitle') else None
        product_data['price'] = soup.find("span", {"class": 'a-price-whole'}).get_text(strip=True) if soup.find("span", {"class": 'a-price-whole'}) else None
        product_data['average_rating'] = soup.find("span", {"class": "a-icon-alt"}).get_text(strip=True) if soup.find("span", {"class": "a-icon-alt"}) else None
        product_data['total_ratings'] = soup.find(id='acrCustomerReviewText').get_text(strip=True) if soup.find(id='acrCustomerReviewText') else None
        product_data['feature_bullets'] = soup.find('div', id='featurebullets_feature_div').get_text(strip=True) if soup.find('div', id='featurebullets_feature_div') else None
        reviews = soup.find_all("span", {"data-hook": "review-body"})
        product_data['reviews'] = [review.get_text(strip=True) for review in reviews] if reviews else None
        return product_data

    def review_parse_func(soup):
        article_content_div = soup.find_all('p', attrs={'data-slot-rendered-content': 'true'})
        article_content = '\n'.join([p.get_text(strip=True) for p in article_content_div])
        return {'Article Content': article_content}

    df = get_data_from_urls(urls, 'title', amazon_parse_func)
    df['label'] = ['Tommaso Forcella', 'Schwinn Phocus 1600', 'Tommaso Imola', 'Schwinn Volare 1400']

    df_2 = get_data_from_urls(bike_exchange_review, 'Article Content', review_parse_func)
    df_2['label'] = ['Tommaso Forcella', 'Tommaso Imola']

    def bikes_insider_parse_func(soup):
        article_content_div = soup.find_all('div', class_='entry-content')
        article_content = '\n'.join([p.get_text(strip=True) for p in article_content_div])
        return {'Article Content': article_content}

    df_3 = get_data_from_urls(bikes_insider_review, 'Article Content', bikes_insider_parse_func)
    df_3['label'] = ['Schwinn Volare 1400']

    def pedal_chef_parse_func(soup):
        article_content_div = soup.find_all('div', class_='rich-text-block w-richtext')
        article_content = '\n'.join([p.get_text(strip=True) for p in article_content_div])
        return {'Article Content': article_content}

    df_4 = get_data_from_urls(pedal_chef_review, 'Article Content', pedal_chef_parse_func)
    df_4['label'] = ['Schwinn Phocus 1600']

    # Concatenate and merge
    combined_df = pd.concat([df_2, df_3, df_4])
    final_df = combined_df.merge(df, on='label')

    return final_df

if __name__ == "__main__":
    result_df = scrape_data()
    print(result_df)
