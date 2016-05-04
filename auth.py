import os, pickle, requests, lxml.html, logging

from settings import USERNAME, PASSWORD, BASE_KAGGLE_URL

def get_authenticated_session():
    """
    get cached or new authenticated session
    """

    if os.path.exists("kaggle_session.pickle"):
        logging.debug("found cached kaggle session")
        with open("kaggle_session.pickle", "rb") as f:
            s = pickle.load(f)
        if not _is_authenticated_session(s):
            logging.debug("kaggle session was no longer authenticated")
            s = _create_authenticated_session()
    else:
        s = _create_authenticated_session()
        logging.debug("caching kaggle session")
        with open("kaggle_session.pickle", "wb") as f:
            pickle.dump(s, f)

    return s

def _is_authenticated_session(s):
    response = s.get(BASE_KAGGLE_URL)
    return _check_response_logged_in(response)

def _create_authenticated_session():

    logging.debug("creating new authenticated kaggle session")

    s = requests.Session()
    auth_payload = {"UserName": USERNAME, "Password": PASSWORD, "JavaScriptEnabled": False}
    response = s.post("https://www.kaggle.com/account/login", data=auth_payload)
    if not _check_response_logged_in(response):
        raise Exception("unable to get authenticated session")
    return s

def _check_response_logged_in(response):
    doc = lxml.html.fromstring(response.content)
    if doc.cssselect("body.logged-in"):
        return True
    else:
        return False