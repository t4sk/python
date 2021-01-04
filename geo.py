from geopy.geocoders import GoogleV3

API_KEY = "AIzaSyBnpms53VlFDJ-d6Vt2GIgKrbgi4PIBxVQ"

g = GoogleV3(API_KEY)
#g.geocode('175 5th Avenue NYC', timeout=10)
g.reverse((36.6225756, 138.5962787, 0.0), timeout=10)
