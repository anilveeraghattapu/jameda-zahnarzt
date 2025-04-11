
import re
from pathlib import Path
import logging
import pandas as pd
import json

import scraper
from dentists import Dentists
from email_crawler import Crawler
from config import settings



output_dir = Path('data')
output_dir.mkdir(exist_ok=True) 

json_file_path = output_dir / 'dentists.jsonl'
xlsx_file_path = output_dir / 'dentists.xlsx'

dentists_list = []
pagenation_urls = []


def safe_text(element, default=''):
    return element.text.strip() if element else default

def safe_find_all(element, selector, index, default=''):
    found = element.find_all(selector)
    return found[index].text.strip() if len(found) > index else default

def scrape_dentist(url):
    soup = scraper.get_soup(url)
    if not soup:
        return

    #searc results
    ul_search = soup.find('ul', attrs={'class': 'list-unstyled search-list', 'data-test-id': 'search-list'})
    for li in ul_search.find_all('li')[0:12]:
        d = Dentists()
        item = li.find('div')
        if item:
            d.doctor =  item.attrs['data-doctor-name']
            d.item_type = item.attrs['data-ga4-entity-type']
            d.url = item.attrs['data-doctor-url']
            scrape_dentist_details(d)
            dentists_list.append(d)

def load_pagenation_urls(n):
    for i in range(1,n+1):
        url = f'https://www.jameda.de/suchen?q=Zahnarzt&page={i}'
        pagenation_urls.append(url)

def get_last_page_index(li):

    li_pages = li.find_all('li')
    try:
        return int(li_pages[-2].text.strip())
    except:
        return 1
    

def scrape_dentist_details(dentist):
    soup = scraper.get_soup(dentist.url)
    if soup:
        #address
        if dentist.item_type == 'doctor':
            address = soup.find('div', attrs = {'class':'media-body', 'data-test-id':'address-info'})
            if address:
                span = address.find('span')
                if span:
                    dentist.praxis = span.text.strip()
                street_span = address.find('span', attrs = {'class':'text-body', 'itemprop':'streetAddress'})
                if street_span:
                    dentist.address = ' '.join(filter(None, [
                        safe_text(street_span.find('span', attrs={'data-test-id': 'address-info-street'})),
                        safe_find_all(street_span, 'a', 0),
                        safe_find_all(street_span, 'a', 1)
                    ])).strip()
        if dentist.item_type == 'clinic':
            praxis = soup.find('h1', attrs={'data-test-id':'facility-header-name'})
            if praxis:
                dentist.praxis = praxis.text.strip()

            divs = soup.find_all('div', class_='mr-1') or []  
            filtered_divs = [d for d in divs if isinstance(d.get('class'), list) and d.get('class') == ['mr-1']]
            if filtered_divs:
                dentist.address = (filtered_divs[0].get_text(strip=True).replace('\n', ' ').replace('\t', '').replace('  ', ' '))
            
            #address = soup.find('div', attrs={'class': 'mr-1'})
            #if address:
            #    dentist.address = address.text.strip().replace('\n', ', ').replace('\t', '')

        #telephone
        phone_anchor = soup.find('a', href=re.compile(r'tel:', re.IGNORECASE)) 
        if phone_anchor:
            dentist.telephone =  phone_anchor.text.strip().replace('\n', '').replace('\t','')
        #website
        if dentist.item_type == 'doctor':
            web_div = soup.find('div', attrs={'class':'www mr-1'})
            if web_div:
                web_anchor = web_div.find('a')
                dentist.website = web_anchor.get('href', '') if web_anchor else ''
        if dentist.item_type == 'clinic':
            about_section = soup.find('section', attrs={'id':'about-section'})
            if about_section:
                web_anchor = about_section.find('a', attrs={'target':'_blank'} )
                dentist.website = web_anchor.get('href', '') if web_anchor else ''

        #emails
        c = Crawler(base_url=dentist.website)
        c.scrape()
        dentist.email = list(c.contacts)


def write_to_json():
    try:
        with open(json_file_path, 'a', encoding='utf-8') as f:
            for dentist in dentists_list:
                f.write(dentist.to_json() + '\n')
    except Exception as e:
        logging.error(f'Exception:Write to JSON: {e}')

def write_to_xlsx():
    try:
        df = pd.read_json(json_file_path, lines=True, encoding='utf-8')
        df.to_excel(str(xlsx_file_path), index=False,engine='openpyxl')
        logging.info(f'Data Exported to XLSX: {Path(xlsx_file_path)}')
    except Exception as e:
        logging.error(f'Exception:Write to excel: {e}')

def scrape():

    url = 'https://www.jameda.de/suchen?q=Zahnarzt'

    soup = scraper.get_soup(url)
    if soup:
        print(soup.title.text)
        #pagenation
        ul_pagination = soup.find('ul', attrs={'class': 'pagination pagination-lg'})
        n = get_last_page_index(ul_pagination)
        load_pagenation_urls(n)
        #load dentists
        for url in pagenation_urls:
            try:
                scrape_dentist(url)
                logging.info(f'extraction completed from: {url}')
            except Exception as e:
                logging.error(f'Error scraping URL {url}: {str(e)}')
                continue 
            
            break
        #write the results to json
        write_to_json()
        write_to_xlsx()
    else:
        logging.error(f'Unable to scrape URL {url}')