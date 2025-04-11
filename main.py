import sys
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src import dentist_scraper as ds
ds.scrape()



# from src.email_crawler import Crawler
# url = 'http://www.zahnarztpraxis-am-tuerltor.de'
# c = Crawler(base_url=url)
# c.scrape()
# print(c.contacts)