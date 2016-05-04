import requests, lxml.html, logging

def accept_rules(s, competition_url, competition_slug):

    rules_accepted_boolean, previous_response = _are_rules_accepted_already(s, competition_url, competition_slug)
    if rules_accepted_boolean:
       return True
    else:
        logging.info("[%s] automatically accepting the rules for competition" % competition_slug)
        doc = lxml.html.fromstring(previous_response.content)
        accept_payload = {
            "__RequestVerificationToken": doc.cssselect("input[name=__RequestVerificationToken]")[0].get('value'),
            "doAccept": doc.cssselect("input[name=doAccept]")[0].get('value'),
        }
        response = s.post(competition_url + "/rules/accept", data=accept_payload)
        if "Thank you for accepting the rules." in response.text:
            logging.info("[%s] rules accepted sucessfully" % competition_slug)
            return True
        else:
            logging.error("[%s] rules were not accepted sucessfully, skipping competition")
            return False

def _are_rules_accepted_already(s, competition_url, competition_slug):
    logging.info("[%s] checking if rules are accepted for competition" % competition_slug)
    response = s.get(competition_url + "/rules")

    if "You accepted these rules" in response.text:
        doc = lxml.html.fromstring(response.content)
        accepted_at = doc.cssselect("#comp-homepage-content > div._buttons > p")[0].text.replace("You accepted these rules at", "")
        logging.info("[%s] rules are accepted already at %s" % (competition_slug, accepted_at))
        return (True, response)
    else:
        logging.info("[%s] rules are not accepted yet" % competition_slug)
        return (False, response)
