from scraper import Scraper

# small wrapper script to run web scraper


def main():
    scraperObj = Scraper.fromCsv("bad_people_lists.csv", "UK_MWL")
    scraperObj.scrapeAllPersons()


if __name__ == "__main__":
    main()
