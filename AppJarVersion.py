import json
import re
from nltk.parse.corenlp import CoreNLPParser
from urllib.request import urlopen
from urllib.parse import urlencode
from stanfordcorenlp import StanfordCoreNLP
from appJar import gui

nlp = StanfordCoreNLP('http://corenlp.run', port=80)
props = {'annotators': 'parse', 'pipelineLanguage': 'en', 'outputFormat': 'json'}
apiEndpointUrl = "https://concept.research.microsoft.com/api/Concept/ScoreByProb"
topK = 10

parser = CoreNLPParser(url='http://corenlp.run')

def submitSentence(value):
    app.label('label', "")
    app.label("score", "")
    app.label("instance", "")
    sentence = app.getEntry("Sentence")

    pos_tagged = nlp.pos_tag(sentence)
    app.updateListBox("list", pos_tagged)

    #cp = nlp.parse(sentence)
    annotated = nlp.annotate(sentence, properties=props)
    #data = json.loads(annotated)

    #print(repr(cp))

    #print(findNP(cp))

    #print(json.dumps(data, indent=4))
    app.label("CP", next(parser.raw_parse("what is orange pie?")).pretty_print())


def findNP(originalString):
    out = []
    for idx in [m.start() for m in re.finditer('\(NP', originalString)]:
        str = ""
        count = 0
        for ch in originalString[ idx+4:]:
            if ch == '(':
                count += 1
            if ch == ')':
                count -= 1
            if count < 0:
                break
            str += ch
        #splitted = str.split('(')


        out.append(str)
    return out


def conceptsFromInstance(instance):
    params = {
        "instance": instance,
        'topK': topK
    }
    url = apiEndpointUrl + '?' + urlencode(params)
    response = json.loads(urlopen(url).read().decode('utf8'))

    return response


def submitInstance(value):

    app.label('label', "")
    # app.clearListBox("list")
    app.label("score", "")
    app.label("instance", "")
    instance = app.getEntry("Instance")
    if not instance.__len__() == 0:
        app.label("instance", instance)
        app.label("score", "by P(c|e)")
        concepts = conceptsFromInstance(instance)
        text = ""
        for key in concepts:
            text += "{:.3f}".format(concepts[key]) + "\t" + key + '\n'

        app.label('label', text)


def update(value):
    listBox = app.listBox('list')

    if not listBox.__len__() == 0:
        concepts = conceptsFromInstance(listBox[0][0])
        app.label("instance", listBox[0][0])
        app.label("score", "by P(c|e)")
        text = ""
        for key in concepts:
            text += "{:.3f}".format(concepts[key]) + "\t" + key + '\n'

        app.label('label', text)


geom = "900x700"
with gui("", bg="teal", geom=geom) as app:
    with app.labelFrame("Sentence", colspan=2, rowspan=1):
        app.entry("Sentence", default="Enter the sentence", sticky='ew', focus=True, submit=submitSentence)
    with app.labelFrame("Single instance", colspan=2, rowspan=1):
        app.entry("Instance", default="Enter single instance", sticky='ew', submit=submitInstance)

    with app.labelFrame("POS tagged:", row=4, column=0, colspan=1, rowspan=1, bg="white"):
        app.listbox("list", submit=update, sticky='news')
    with app.labelFrame("Concept distributions:", row=4, column=1, colspan=1, rowspan=1, bg="white"):
        app.label("instance", "", row=4, sticky='nw')
        app.label("score", "", row=4, sticky='n')
        app.label("label", "", colspan=2, sticky='nw')
    with app.labelFrame("Constituency Parsing: ", row=5, column=0, colspan=1, rowspan=1, bg="white"):
        app.label("CP", "", row=5, sticky='nw')
    with app.labelFrame("Answer: ", row=5, column=1, colspan=1, rowspan=2, bg="white"):
        app.label("answer", "", colspan=1, sticky='ne')


nlp.close()