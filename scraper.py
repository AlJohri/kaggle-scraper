import os, requests, lxml.html, logging

from settings import DRYRUN, BASE_KAGGLE_URL
from auth import get_authenticated_session
from rules import accept_rules

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARN)

os.makedirs("data", exist_ok=True)

competition_urls = [
    "https://www.kaggle.com/c/painter-by-numbers",
    "https://www.kaggle.com/c/facial-keypoints-detection",
    "https://www.kaggle.com/c/street-view-getting-started-with-julia",
    "https://www.kaggle.com/c/expedia-hotel-recommendations",
    "https://www.kaggle.com/c/sf-crime",
    "https://www.kaggle.com/c/state-farm-distracted-driver-detection",
    "https://www.kaggle.com/c/draper-satellite-image-chronology"
]

s = get_authenticated_session()

for competition_url in competition_urls:
    competition_slug = competition_url.replace("https://www.kaggle.com/c/", "")
    logging.info("[%s] scraping competition started" % competition_slug)

    os.makedirs("data/{}".format(competition_slug), exist_ok=True)

    if not accept_rules(s, competition_url, competition_slug):
        break

    logging.info("[%s] attempting to find data files for competition" % competition_slug)
    response = s.get(competition_url + "/data")
    doc = lxml.html.fromstring(response.content)

    num_files = len(doc.cssselect("td.file-name"))
    if num_files > 0:
        file_names = ", ".join([x.text_content() for x in doc.cssselect("td.file-name")])
        logging.info("[%s] %d data files found: %s" % (competition_slug, num_files, file_names))
    else:
        logging.error("[%s] could not find data files, skipping competition" % competition_slug)
        continue

    for i, td_file_name in enumerate(doc.cssselect("td.file-name")):
        file_name = td_file_name.text_content()
        file_link = BASE_KAGGLE_URL + td_file_name.getnext().cssselect("a")[0].get("href")

        logging.info("[%s] downloading # %s %s" % (competition_slug, i, file_name))

        if DRYRUN:
            logging.info("[%s] DRY RUN performing head request instead of get request for %s %s" % (competition_slug, i, file_name))
            response = s.head(file_link, allow_redirects=True)
            real_url = response.url
            logging.info("[%s] real url for %s %s is %s" % (competition_slug, i, file_name, real_url))
        else:
            response = s.get(file_link)
            if response.status_code != 200:
                logging.error("[%s] request for # %s %s was not sucessful with error code %s, skipping competition" % (competition_slug, i, file_name, response.status_code))
                break
            file_location = "data/{}/{}".format(competition_slug, file_name)
            logging.info("[%s] sucessfully downloaded %s %s" % (competition_slug, i, file_name))
            logging.info("[%s] writing file to disk at %s" % (competition_slug, file_location))
            with open(file_location, "wb") as f:
                f.write(response.content)
