import pandas as pd
from urllib import request
import re
from lxml import etree, html
import urllib.parse

# url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area[]=1101&area[]=1102&area[]=1103&area[]=1104&area[]=1105&area[]=1106&area[]=1107&area[]=1108&area[]=1109&area[]=1110&newly=&price_from=&price_to=&gross_from=&gross_to=&dim[]=1002&dim[]=1004&year=&b_area_from=&b_area_to=&houses_ge=&houses_le=&min=&l_area_from=&l_area_to=&keyword=&ex_real_search="
url = "https://www.rakumachi.jp/syuuekibukken/area/prefecture/dimAll/?area%5B%5D=1&newly=&price_from=&price_to=&gross_from=&gross_to=&dim%5B%5D=1002&dim%5B%5D=1004&year=&b_area_from=&b_area_to=&houses_ge=&houses_le=&min=&l_area_from=&l_area_to=&keyword=&ex_real_search="

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3'
}

GREEN = '\x1b[32;21m'
PURPLE = '\x1b[32;35m'
RESET = '\x1b[0m'


def debug(*msg):
    print(PURPLE, *msg, RESET)


def get_html(url):
    try:
        req = request.Request(url, headers=HEADERS)
        f = request.urlopen(req, timeout=60)
    except Exception as e:
        debug(e, url)

    assert(f.status == 200)
    
    charset = f.headers.get_content_charset()
    raw = f.read().decode(charset, errors="replace")

    return html.fromstring(raw)


# get node with house info
INFO_RULE = '//div[@class="propertyBlock__contentRight"]'
# easier to just get 'rendered text' with .text_content() then use regex
# partial implementation
REGEX_MAP = {
    "price": r"(?<=価格).+\s([\d\w]+万)(?:\s+)?(?=円)",
    "yield": r"(?<=利回り).+\s([\d\.%]+)(?=\s)",
    "address": r"(?<=所在地)(.*)(?=沿線交通)",
    "date_of_construction": r"(?<=築年月)(.*)(?=総戸数)",
    "total_units": r"(?<=総戸数)(.*)(?=建物構造)",
    "building_structure": r"(?<=建物構造)(.*)(?=建物面積)",
    "building_area": r"(?<=建物面積)[\s]+([\d\.]+)(?=㎡)",
    "num_floors": r"(?<=階数)(.*)(?=土地面積)",
    "land_area": r"(?<=土地面積)[\s]+([\d\.]+)(?=㎡)"
}

def get_data(page):
    results = []
    for info in page.xpath(INFO_RULE):
        txt = info.text_content().replace("\n", "")
        data = {}
        for k, v in REGEX_MAP.items():
            m = re.search(v, txt, flags=re.MULTILINE)
            if m:
                data[k] = m.group(1).strip()
        results.append(data)
    return results

### main ###
parts = urllib.parse.urlparse(url)
base_url = "{}://{}{}".format(parts.scheme, parts.netloc, parts.path)

first_page = get_html(url)

LINKS_TO_MORE_PAGES = '//div[@class="header_pager_navigation"]//li[contains(@id, "pagination_page_")]/a/@href'
links = first_page.xpath(LINKS_TO_MORE_PAGES)
# go to other pages(links) found in 1st page
results = []
i = 1
for link in links:
    print("page", i)
    i += 1
    page = get_html(base_url + link)
    results.extend(get_data(page))

pd.DataFrame(results).to_csv("rakumachi.csv", index=False)
