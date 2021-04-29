import csv
import json
import logging
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

REQUEST_DELAY = 2
HTML_PARSER = "lxml"


class Scraper:

    """Web scraper to retrieve details about each person listed at
    https://www.nationalcrimeagency.gov.uk/most-wanted-search
    """

    def __init__(
        self,
        sourceCode: str,
        sourceName: str,
        sourceUrl: str,
        requestDelay: Optional[int] = None,
        outputFile: Optional[str] = None,
    ):
        """Initialize Scraper object with user-provided values

        :sourceCode: website code from bad_people_lists.csv
        :sourceName: website name from bad_people_lists.csv
        :sourceUrl: website URL from bad_people_lists.csv (NOTE: in practice, must be
        https://www.nationalcrimeagency.gov.uk/most-wanted-search for scraper to
        function, but left as an argument for modularity)
        :requestDelay: optional, how long to wait in between HTTP requests to website
        in seconds. Defaults to 2 seconds
        :outputFile: optional, path to JSON file to which data will be written.
        Defaults to <sourceCode>_persons.json

        """
        self.sourceCode = sourceCode
        self.sourceName = sourceName
        self.sourceUrl = sourceUrl

        self.requestDelay = REQUEST_DELAY if requestDelay is None else requestDelay

        self.outputFile = (
            f"{self.sourceCode}_persons.json" if outputFile is None else outputFile
        )

        self.htmlParser = HTML_PARSER

        self.personsDict = {
            "source_code": self.sourceCode,
            "source_name": self.sourceName,
            "source_url": self.sourceUrl,
            "persons": [],
        }

        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

    def prepareBeautifulSoup(self, url: str) -> BeautifulSoup:
        """Create BeautifulSoup object for HTML content returned by given URL. Only
        meant to be called by other methods.

        :url: URL from which to create a BeautifulSoup object
        :returns: BeautifulSoup object of given URL's response

        """
        page = requests.get(url)
        page.raise_for_status()

        soupObject = BeautifulSoup(page.text, self.htmlParser)

        return soupObject

    def getDetailPageLinks(self) -> List[str]:
        """Return list of links to individual criminal pages listed on home page

        :returns: list of links to all individual pages

        """
        soupObj = self.prepareBeautifulSoup(self.sourceUrl)
        resultsContainer = soupObj.select_one("dl.search-results")
        personBoxes = resultsContainer.select("div.span4")
        personAnchors = [box.find("a") for box in personBoxes]

        pageUrlParse = urlparse(self.sourceUrl)
        pageDomain = f"{pageUrlParse.scheme}://{pageUrlParse.netloc}"

        return [pageDomain + anchor["href"] for anchor in personAnchors]

    def getColumnInfo(
        self, columnSoupObj: BeautifulSoup, pageUrl: str
    ) -> Dict[str, str]:
        """Return information listed in one column of an individual criminal's page as a
        dictionary

        :columnSoupObj: BeautifulSoup object of the column div
        :pageUrl: URL of page
        :returns: dictionary of column's information

        """
        columnDict = {}
        infoSpans = columnSoupObj.find_all("span")

        for infoIndex in range(0, len(infoSpans), 2):
            infoKeyText = infoSpans[infoIndex].get_text()
            infoKey = infoKeyText.strip(": ").lower().replace(" ", "_")

            try:
                infoValue = infoSpans[infoIndex + 1].get_text().strip()

                columnDict[infoKey] = infoValue
            except IndexError:
                self.logger.info(
                    f"No matching value for {infoKey} at {pageUrl}, skipping"
                )

        return columnDict

    def getIndividualDetails(self, pageUrl: str):
        """Retrieve all available information about criminal from individual page as a
        dictionary and add it to the "persons" filde of self.personsDict

        :pageUrl: URL of page
        :returns: None

        """
        soupObj = self.prepareBeautifulSoup(pageUrl)
        infoDict = {}
        infoContainer = soupObj.select_one("div.item-page.most-wanted-grid")

        nameHeader = infoContainer.select_one('h2[itemprop="headline"]')
        fullName = nameHeader.get_text().strip()
        lastSpaceInd = fullName.rindex(" ")
        infoDict["firstname"] = fullName[:lastSpaceInd].strip()
        infoDict["lastname"] = fullName[lastSpaceInd:].strip()

        summaryContainer = infoContainer.select_one('div[itemprop="articleBody"]')
        infoDict["general"] = summaryContainer.get_text().strip()

        selectors = {
            "crime": "div.most-wanted-basic",
            "about": "div.most-wanted-description",
            "other": "div.most-wanted-additional",
        }

        for key, selector in selectors.items():
            columnContainer = infoContainer.select_one(selector)
            infoDict[key] = self.getColumnInfo(columnContainer, pageUrl)

        self.personsDict["persons"].append(infoDict)

    def scrapeAllPersons(self, writeToFile: Optional[bool] = True):
        """Scrape entire source URL for information about each criminal. This is the
        main method that users should call

        :writeToFile: optional, whether to write scraped data to outputFile specified in
        constructor, or only popuplate self.personsDict without saving data anywhere
        else. Defaults to True
        :returns: None

        """
        self.logger.info(f"Beginning scrape using {self.sourceUrl} as main page")

        individualLinks = self.getDetailPageLinks()

        self.logger.info(
            f"Retrieved {len(individualLinks)} individual links from {self.sourceUrl}"
        )

        for link in individualLinks:
            time.sleep(self.requestDelay)

            self.logger.info(f"Scraping {link}")

            self.getIndividualDetails(link)

        if writeToFile:
            with open(self.outputFile, "w") as f:
                json.dump(self.personsDict, f, indent=4)

            self.logger.info(f"Wrote results to {self.outputFile}")

        self.logger.info("Scrape complete")

    @classmethod
    def fromCsv(
        cls,
        filePath: str,
        sourceCode: str,
        requestDelay: Optional[int] = None,
        outputFile: Optional[str] = None,
    ) -> Dict[str, str]:
        """Alternative constructor to instantiate Scraper object from
        bad_people_lists.csv file

        :filePath: path to bad_people_lists.csv or other file of same format
        :sourceCode: source code for correct URL, as listed in bad_people_lists.csv. In
        practice, should be "UK_MWL" but left as an argument for modularity
        :requestDelay: optional, how long to wait in between HTTP requests to website
        in seconds. Defaults to 2 seconds
        :outputFile: optional, path to JSON file to which data will be written.
        Defaults to <sourceCode>_persons.json
        :returns: Scraper object with values from bad_people_lists.csv

        """
        fileHandle = open(filePath)
        csvReader = csv.DictReader(fileHandle, skipinitialspace=True)

        for line in csvReader:
            if line["source_code"] == sourceCode:
                sourceName = line["source_name"]
                sourceUrl = line["source_url"]
                fileHandle.close()

                return cls(
                    sourceCode,
                    sourceName,
                    sourceUrl,
                    requestDelay=requestDelay,
                    outputFile=outputFile,
                )

        raise Exception(f"source_code {sourceCode} not found in {filePath}")
