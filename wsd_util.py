#!/usr/bin/python

from sys import stdin
from httplib import HTTPConnection
from urllib import urlencode, urlretrieve
from json import loads


# Adapted from http://www.websequencediagrams.com/embedding.html
def wsd_image_url(diagram, style="qsd"):
    request_body = urlencode({
        "message": diagram,
        "style": style,
        "apiVersion": "1"})

    conn = HTTPConnection("www.websequencediagrams.com")
    conn.request("POST", "/", request_body)
    response = conn.getresponse()

    if response.status != 200:
        raise WsdException(
            "Invalid response code: %s" % response.status)

    result = loads(response.read())

    if result['errors']:
        raise WsdException(
            "Invalid response: %s" % result['errors'])

    return result['img']


class WsdException(Exception):
    def __init__(self, *args, **kwargs):
        super(WsdException, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    wsd = stdin.read()
    img = wsd_image_url(wsd)
    if not img:
        print "Error retrieving wsd."
    else:
        urlretrieve("http://www.websequencediagrams.com/" + img, "wsd.png")


