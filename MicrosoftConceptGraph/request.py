import json
import operator
from urllib.request import urlopen
from urllib.parse import urlencode

ScoreByCross = 'ScoreByCross'
ScoreByProb = "ScoreByProb"
ScoreTypes = {ScoreByCross :"Score by BLC", ScoreByProb: "Score by P(c|e)" }
ScoreType = ScoreByCross

apiEndpointUrl = "https://concept.research.microsoft.com/api/Concept/"
topK = 20

def setScoreType(scoreType):
    global ScoreType
    ScoreType = scoreType


def conceptsFromInstance(instance):
    params = {
        "instance": instance,
        'topK': topK
    }
    url = apiEndpointUrl + ScoreType + '?' + urlencode(params)
    response = json.loads(urlopen(url).read().decode('utf8'))
    return response

def getConcept(sent):
    print("Concept request ",end="")
    print("<" + sent + ">")
    print(ScoreTypes[ScoreType] )
    concepts = conceptsFromInstance(sent)

    print( sorted(concepts.items(), key=operator.itemgetter(1),reverse=True))
    max = 0
    text = ()

    for key in concepts:
        if concepts[key] > max:
            max = concepts[key]
            text = ("{:.3f}".format(concepts[key]), key)

    if not concepts:
        text=(0,"No concepts")
    return text

def getScoreType():
    return ScoreTypes[ScoreType]