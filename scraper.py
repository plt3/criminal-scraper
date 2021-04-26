import csv
import json
import logging
import time
from typing import Dict, List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

CSV_PATH = "bad_people_lists.csv"
SOURCE_CODE = "UK_MWL"
OUTPUT_PATH = f"{SOURCE_CODE}_persons.json"
REQUEST_SLEEP = 2

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def prepareBeautifulSoup(url: str) -> BeautifulSoup:
    """TODO: Docstring for prepareBeautifulSoup.

    :url: TODO
    :returns: TODO

    """
    page = requests.get(url)
    page.raise_for_status()

    soupObject = BeautifulSoup(page.text, "lxml")

    return soupObject


def getDetailPageLinks(pageUrl: str) -> List[str]:
    """TODO: Docstring for getDetailPageLinks.

    :pageUrl: TODO
    :returns: TODO

    """
    soupObj = prepareBeautifulSoup(pageUrl)
    resultsContainer = soupObj.select_one("dl.search-results")
    personBoxes = resultsContainer.select("div.span4")
    personAnchors = [box.find("a") for box in personBoxes]

    pageUrlParse = urlparse(pageUrl)
    pageDomain = f"{pageUrlParse.scheme}://{pageUrlParse.netloc}"

    return [pageDomain + anchor["href"] for anchor in personAnchors]


def getColumnInfo(columnSoupObj: BeautifulSoup) -> Dict[str, str]:
    """TODO: Docstring for getColumnInfo.

    :columnSoupObj: TODO
    :returns: TODO

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
            pass

    return columnDict


def getIndividualDetails(pageUrl: str):
    """TODO: Docstring for getIndividualDetails.

    :pageUrl: TODO
    :returns: TODO

    """
    soupObj = prepareBeautifulSoup(pageUrl)
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
        infoDict[key] = getColumnInfo(columnContainer)

    return infoDict


def createDict(filePath: str, sourceCode: str) -> Dict[str, str]:
    """TODO: Docstring for createDict.

    :filePath: TODO
    :sourceCode: TODO
    :returns: TODO

    """
    fileHandle = open(filePath)
    csvReader = csv.DictReader(fileHandle, skipinitialspace=True)

    for line in csvReader:
        if line["source_code"] == sourceCode:
            fileHandle.close()
            line["persons"] = []

            logging.info("Scraping " + line["source_url"] + " as main list of persons")

            return line

    raise Exception(f"source_code {sourceCode} not found in {filePath}")


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    logging.info("Begin scrape")

    jsonObj = createDict(CSV_PATH, SOURCE_CODE)
    individualLinks = getDetailPageLinks(jsonObj["source_url"])

    logging.info(
        f"Retrieved {len(individualLinks)} individual links from "
        + jsonObj["source_url"]
    )

    for link in individualLinks:
        time.sleep(REQUEST_SLEEP)

        logging.info(f"Scraping {link}")

        personObj = getIndividualDetails(link)
        jsonObj["persons"].append(personObj)

    logging.info(f"Writing results to {OUTPUT_PATH}")

    with open(OUTPUT_PATH, "w") as f:
        json.dump(jsonObj, f, indent=4)

    logging.info("Scrape complete")


if __name__ == "__main__":
    main()
