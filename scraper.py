from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def prepareBeautifulSoup(url: str) -> BeautifulSoup:
    """TODO: Docstring for prepareBeautifulSoup.

    :url: TODO
    :returns: TODO

    """
    # page = requests.get(url)
    # page.raise_for_status()
    with open("page.html") as f:
        text = f.read()

    # soupObject = BeautifulSoup(page.text, "lxml")
    soupObject = BeautifulSoup(text, "lxml")

    return soupObject


def getDetailPageLinks(soupObj: BeautifulSoup, pageUrl: str) -> List[str]:
    """TODO: Docstring for getDetailPageLinks.

    :soupObj: TODO
    :pageUrl: TODO
    :returns: TODO

    """
    resultsContainer = soupObj.select_one("dl.search-results")
    personBoxes = resultsContainer.select("div.span4")
    personAnchors = [box.find("a") for box in personBoxes]

    pageUrlParse = urlparse(pageUrl)
    pageDomain = f"{pageUrlParse.scheme}://{pageUrlParse.netloc}"

    return [pageDomain + anchor["href"] for anchor in personAnchors]


def main():
    """TODO: Docstring for main.
    :returns: TODO

    """
    url = "https://www.nationalcrimeagency.gov.uk/most-wanted-search"
    soup = prepareBeautifulSoup("placeholder")
    return getDetailPageLinks(soup, url)


if __name__ == "__main__":
    a = main()
