import pandas as pd
import altair as alt
#from vega_datasets import data

uf = pd.read_csv("results.csv")
def parsePrice(p):
    if "億" in p:
        p = p.replace("億", "")
    if "万" in p:
        return p.replace("万", "")
    return p # should not happen

uf["amount"] = uf.price.apply(parsePrice).astype(float)

# get "ku"
uf["ku"] = uf.address.str.extract("(?<=市)(.*)(?=区)")

chart = alt.Chart(uf).mark_circle(size=60).encode(
        x='amount',
        y='land_area',
        color='ku',
        tooltip=['ku', 'amount', 'land_area', 'gross']
        ).properties(
                width=1000,
                height=600
                )

chart.save("scatter.html")
!xdg-open scatter.html






# need more work, example https://altair-viz.github.io/gallery/choropleth.html

### map data
names = pd.read_csv("cities_in_japan_2019.csv") # mapping: name of location to topological map 
uf
unique_cities = names.drop_duplicates("city_ja",keep="first")
mapCityNameToId = {r.city_ja: r["id"] for _, r in unique_cities[["city_ja", "id"]].iterrows()}
citylist = list(mapCityNameToId.keys())

def searchCityId(address):
    for name in citylist:
        if name in address:
            return mapCityNameToId[name]
    return None

show = uf[["address", "amount"]] # filter data
show["id"] = show.address.apply(searchCityId)
show


cities = alt.topo_feature("japan-2017-topo.json", "cities")

#counties = alt.topo_feature(data.us_10m.url, 'counties')
#source = data.unemployment.url

show["id"].value_counts() # all sapporo

medprice = show.groupby("id").amount.median().reset_index()
medprice


topochart = alt.Chart(cities).mark_geoshape().encode(
    color='amount:Q'
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(medprice, 'id', ['amount'])
).project(
    type='albersUsa'
).properties(
    width=500,
    height=300
)

topochart.save("map.html")
!xdg-open map.html


