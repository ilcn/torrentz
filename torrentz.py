from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urlencode


class Result:
    """docstring for Result"""

    def __init__(self):
        self.titles = {}
        self.creations_times = {}
        self.sizes = {}
        self.peers = {}
        self.leechers = {}
        self.retrieved_times = {}
        self.magnet_links = {}
        self.trackers = {}

    def print_all(self):
        for x in self.titles.keys():
            print(self.titles[x], self.creations_times[x], self.sizes[x], self.peers[
                  x], self.leechers[x], self.retrieved_times[x], self.magnet_links[x], self.trackers[x])

    def get(self, infohash):
        try:
            oneresult = {"title": self.titles[infohash]}
            oneresult["creation_time"] = self.creations_times[infohash]
            oneresult["size"] = self.sizes[infohash]
            oneresult["peers"] = self.peers[infohash]
            oneresult["leechers"] = self.leechers[infohash]
            oneresult["retrieved_time"] = self.retrieved_times[infohash]
            oneresult["magnet_link"] = self.magnet_links[infohash]
            oneresult["infohash"] = infohash
            oneresult["trackers"] = self.trackers[infohash]

            for x in oneresult.values():
                if x is None:
                    return None
        except Exception as e:
            oneresult = None
            print("result set to None due to the following exception")
            raise e
        return oneresult


def add_trackers(result):
    """
    takes in result with no tracker information,
    returns one with link with trackers
    """
    for infohash in result.titles.keys():
        uri = urljoin("https://torrentz2.eu/", infohash)
        trackers = []
        soup = BeautifulSoup(requests.get(uri).text, "html.parser")
        dt_data = soup.find_all("dt")
        for d in dt_data:
            link = d.text
            if link[0:3] == 'udp' or link[0:4] == 'http' and link[len(link) - 8:len(link)] == "announce":
                trackers.append(link)
        # print(trackers)
        result.trackers[infohash] = trackers
        dn = urlencode(dict(dn=result.titles[infohash]))
        trs = '&'.join(map(lambda t: urlencode(dict(tr=t)), trackers))
        uri = 'magnet:?xt=urn:btih:%s&%s&%s' % (infohash, dn, trs)
        result.magnet_links[infohash] = uri
    return result


def search(term):
    r = requests.get("https://torrentz2.eu/search?f=" + term)
    data = r.text
    soup = BeautifulSoup(data, "html.parser")

    # print(soup.prettify())
    dl_data = soup.find_all("dl")

    print(len(dl_data))
    result = Result()
    for x in dl_data:
        # print(x,type(x))
        linkandtitle = x.find_all('a', href=True)
        for lt in linkandtitle:
            # print(lt["href"], lt.text)
            # print('here')
            infohash = lt["href"].strip('/')
            result.titles[infohash] = lt.text
            # print(infohash, titles[infohash])
            spans = x.find_all('span')
            result.creations_times[infohash] = spans[1]["title"]
            result.sizes[infohash] = spans[2].text
            result.peers[infohash] = spans[3].text
            result.leechers[infohash] = spans[4].text
            result.retrieved_times[infohash] = int(time.time())

    # result.print_all()
    return add_trackers(result)


if __name__ == "__main__":
    result = search("star")
    # result.print_all()
