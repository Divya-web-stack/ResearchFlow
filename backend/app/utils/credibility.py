def get_source_score(url: str):

    url = url.lower()

    if ".gov" in url:
        return 95, "Very High"

    elif ".edu" in url:
        return 90, "High"

    elif "nih.gov" in url:
        return 98, "Very High"

    elif "nature.com" in url:
        return 95, "Very High"

    elif "thelancet.com" in url:
        return 95, "Very High"

    elif "nejm.org" in url:
        return 95, "Very High"

    elif "sciencedirect.com" in url:
        return 90, "High"

    elif "springer.com" in url:
        return 90, "High"

    elif "ieee.org" in url:
        return 90, "High"

    elif "acm.org" in url:
        return 90, "High"

    elif "weforum.org" in url:
        return 85, "High"

    elif "who.int" in url:
        return 95, "Very High"

    elif "openai.com" in url:
        return 85, "High"

    elif "google.com" in url:
        return 85, "High"

    elif "microsoft.com" in url:
        return 85, "High"

    elif "reddit.com" in url:
        return 60, "Low"

    elif "quora.com" in url:
        return 55, "Low"

    return 70, "Medium"