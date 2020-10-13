
import pandas as pd
from urllib import request
import re
from lxml import etree, html
import urllib.parse

url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area[]=1101&area[]=1102&area[]=1103&area[]=1104&area[]=1105&area[]=1106&area[]=1107&area[]=1108&area[]=1109&area[]=1110&newly=&price_from=&price_to=&gross_from=&gross_to=&dim[]=1002&dim[]=1004&year=&b_area_from=&b_area_to=&houses_ge=&houses_le=&min=&l_area_from=&l_area_to=&keyword=&ex_real_search="

Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

H = {'User-Agent': Agent, 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'}

GREEN = '\x1b[32;21m'
PURPLE = '\x1b[32;35m'
RESET = '\x1b[0m'


def debug(*msg):
    print(PURPLE, *msg, RESET)


def get_page(url):
    try:
        req = request.Request(url, headers=H)
        f = request.urlopen(req, timeout=60)
    except Exception as e:
        debug(e, url)

    assert(f.status == 200)
    charset = f.headers.get_content_charset()
    charset
    raw = f.read()

    return raw.decode(charset, errors="replace")


parts = urllib.parse.urlparse(url)
base_url = "{}://{}{}".format(parts.scheme, parts.netloc, parts.path)

# main/1st page
raw = get_page(url)
houses = html.fromstring(raw)

# get node with house info
info_rule = '//div[@class="propertyBlock__contentRight"]'
# easier to just get 'rendered text' with .text_content() then use regex
# partial implementation
regex_map = {
    "price": r"(?<=価格).+\s([\d\w]+万)(?:\s+)?(?=円)",
    "gross": r"(?<=利回り).+\s([\d\.%]+)(?=\s)",
    "address": r"(?<=所在地)(.*)(?=沿線交通)",
    "floor_area": r"(?<=建物面積)[\s]+([\d\.]+)(?=㎡)",
    "land_area": r"(?<=土地面積)[\s]+([\d\.]+)(?=㎡)"
}


def get_data(houses):
    results = []
    for info in houses.xpath(info_rule):
        txt = info.text_content().replace("\n", "")
        data = {}
        for k, v in regex_map.items():
            m = re.search(v, txt, flags=re.MULTILINE)
            if m:
                data[k] = m.group(1).strip()
        results.append(data)
    return results


# first page results 20
results = get_data(houses)
print(len(results))

# this should really be parallelized into different processes
links_to_more_pages = '//div[@class="header_pager_navigation"]//li[contains(@id, "pagination_page_")]/a/@href'
# go to other pages(links) found in 1st page
for u in houses.xpath(links_to_more_pages):
    u = base_url + u
    raw = get_page(u)
    houses = html.fromstring(raw)
    results.extend(get_data(houses))

print(len(results))


units = pd.DataFrame(results)
units.to_csv("rakumachi.csv", index=False)
