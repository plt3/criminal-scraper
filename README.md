# criminal-scraper

> requests/bs4 web scraper to retrieve "Most Wanted" data

## Installation:

NOTE: tested for macOS, but installation on Linux or Windows should be similar.
Requirements: Python 3.6+, pip

- Clone repo with `git clone https://github.com/plt3/criminal-scraper`
- Navigate to project directory with `cd criminal-scraper`
 Recommended: create virtual environment: `python3 -m venv venv` and activate it: `source venv/bin/activate`
- Install dependencies with `pip install -r requirements.txt`

## Usage:

- In project home directory, run scraper with `python3 runScraper.py`
- If source code is not changed, this will write data to `UK_MWL_persons.json` in project home directory (although the file is already included in this repository anyways)
- Can override many defaults (output JSON file path, HTTP request delay) by passing extra arguments to either of the scraper's constructors. See Scraper class's source code for more information.
- Example of overriding output file path and HTTP request delay:

```python
from scraper import Scraper

scraperObj = Scraper.fromCsv("bad_people_lists.csv", "UK_MWL", requestDelay=10, outputFile="/path/to/file.json")
scraperObj.scrapeAllPersons()
```
