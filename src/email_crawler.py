import re
from urllib.parse import urljoin, urlparse, urlunparse
import scraper
from collections import deque

class Crawler():
    def __init__(self, base_url):
        self.__base_url = base_url
        self.__internal_urls = set()
        self.contacts = set()
        
    
    def __get_scheme(self, url):
        return urlparse(url).scheme
    
    def __get_netloc(self, url):
        return urlparse(url).netloc
    
    def __get_path(self,url):
        return urlparse(url).path
    
    
    def __is_html(self, url):
        parsed = urlparse(url)
        return not parsed.path.rstrip('/').lower().split('.')[-1] in {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'pdf', 'zip', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'mp3', 'mp4'
        }

    def __is_internal(self, url):
        url_netloc = self.__get_netloc(url)
        if not url_netloc:
            return True
        return url_netloc == self.__get_netloc(self.__base_url)
    
    def __construct_url(self, url):
        scheme = self.__get_scheme(self.__base_url)
        netloc = self.__get_netloc(self.__base_url)
        path = self.__get_path(url).strip('/')
        return f'{scheme}://{netloc}/{path}'.rstrip('/')

    def __is_visited(self, url):
        normalized = self.__construct_url(url)
        return normalized in self.__internal_urls

    def __is_valid(self, url):
        if url.startswith(('tel:', 'mailto:', 'javascript:')) or '@' in url:
            return False
        return True

    def __extract_links(self, max_depth = 1):
               
        queue = deque([(self.__base_url,0)])
        while queue:
            url, depth = queue.popleft()
            url = url.rstrip('/')

            if depth > max_depth:  
                continue
            if not self.__is_visited(url):
                self.__internal_urls.add(self.__construct_url(url))
                soup = scraper.get_soup(url)
                if soup:
                    for a in soup.find_all('a', href=True):
                        link = a.attrs['href']
                        a_link = self.__construct_url(link)
                        if self.__is_internal(link) and self.__is_html(link) and self.__is_valid(link) and a_link not in self.__internal_urls:
                            queue.append((a_link,depth+1))    
       

    def __extract_emails(self):
        for url in sorted(self.__internal_urls):
            soup = scraper.get_soup(url)
            if soup:

                # 1. Extract emails from mailto: links
                for a in soup.find_all('a', href=True):
                    if a['href'].lower().startswith('mailto:'):
                        email = a['href'][7:].split('?')[0] 
                        if '@' in email: 
                            self.contacts.add(email.lower().strip())

                emails = re.findall(
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                    soup.body.get_text(separator=' ', strip=True),
                    re.IGNORECASE
                )
                self.contacts.update(e.lower().strip() for e in emails)

    def scrape(self):
        self.__extract_links()
        self.__extract_emails()