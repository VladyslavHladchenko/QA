from urllib.request import urlopen
from urllib.parse import urlencode
import json

GoogleKGURL= "https://kgsearch.googleapis.com/v1/entities:search"
API_KEY = "AIzaSyBLhn9xTY9NynDihbQeG9qAe0BQAY2UwwY"

def knowlege_graph_request(query,c0):
    params = {
        "query": query,
        'key' : API_KEY,
        'limit' : 10,
        'indent' : True
    }
    url = GoogleKGURL + "?" + urlencode(params)
    response = json.loads(urlopen(url).read().decode('utf8'))
    print("Google request <" + query + ">")
    itemListElement = response['itemListElement']

    print(json.dumps(itemListElement,indent=4))
    for item in itemListElement:
#        print(item['result'].keys())
#        if 'detailedDescription' in item['result'].keys():
#            print("detailedDescription:" )
#            print(item['result']["detailedDescription"]['articleBody'])
        if "description" in item['result'].keys():
            #print("description:")
            print(item["resultScore"], end = " ")
            print(item['result']["description"])