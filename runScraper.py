from scraper import Scraper


def main():
    scraperObj = Scraper.fromCsv("bad_people_lists.csv", "UK_MWL")
    scraperObj.scrapeAllPersons()


if __name__ == "__main__":
    main()
