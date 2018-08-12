import random
import os

def get_ad(level=0):
    """return an ad source from dir"""
    # placeholder
    urls = []
    # base dir
    dir = "static/img/ads/"

    # iterate through files
    for filename in os.listdir(dir):
        # if filename end in .jpg
        if filename.endswith(".jpg"):
            # check if none
            if not None:
                # set full url
                url = os.path.join(dir, filename)
                # check for level down
                if level == 1:
                    # if level down add ../
                    url = "../"+url
                # append to placeholder
                urls.append(url)
            continue
        else:
            continue
    # choose random ad src
    return random.choice(urls)
