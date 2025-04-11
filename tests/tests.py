import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from src import dentist_scraper as ds
ds.write_to_xlsx()

#print('tests module')