import operator
import nltk.parse.corenlp as CoreNLP
import json
from urllib.request import urlopen
from urllib.parse import urlencode
from nltk.draw.util import CanvasFrame, BoxWidget, TextWidget
from nltk.draw.tree import TreeWidget, TreeSegmentWidget
from tkinter.font import Font
from tkinter import Entry, Button, Text, Tk, LEFT, RIGHT, INSERT, CURRENT, END, Label, ACTIVE, BOTTOM, StringVar, NE,NW
from itertools import cycle

interest = ("NP","NN","NNS","NNP","NNPS")

def print_class_name(smth):
    print(smth.__class__.__name__)

def get_subsentence(element,s):
    for st in element.subtrees():
        global subsentence
        if type(st) is TreeSegmentWidget:
            get_subsentence(st,s)
        elif type(st) is TextWidget:
            s.append(st._text)

def setScoreType(scoreType):
    global ScoreType
    ScoreType = scoreType

ScoreByCross = 'ScoreByCross'
ScoreByProb = "ScoreByProb"
ScoreTypes = {ScoreByCross :"Score by BLC", ScoreByProb: "Score by P(c|e)" }
ScoreType = ScoreByCross

apiEndpointUrl = "https://concept.research.microsoft.com/api/Concept/"
topK = 20
GoogleKGURL= "https://kgsearch.googleapis.com/v1/entities:search"
API_KEY = "AIzaSyBLhn9xTY9NynDihbQeG9qAe0BQAY2UwwY"

def Google(query):
    params = {
        "query": query,
        'key' : API_KEY,
        'limit' : 10,
        'indent' : True
    }
    url = GoogleKGURL + "?" + urlencode(params)
    response = json.loads(urlopen(url).read().decode('utf8'))
    print("Google request <" + query + ">")
    print(json.dumps(response['itemListElement'],indent=4))


def _conceptsFromInstance(instance):
    params = {
        "instance": instance,
        'topK': topK
    }
    url = apiEndpointUrl + ScoreType + '?' + urlencode(params)
    response = json.loads(urlopen(url).read().decode('utf8'))
    return response

def _getConcept(sent):
    print("Concept request ",end="")
    print("<" + sent + ">")
    print(ScoreTypes[ScoreType] )
    concepts = _conceptsFromInstance(sent)

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

def _getConcepts(sent):
    concepts = _conceptsFromInstance(sent)
    text = ""
    for key in concepts:
        text += " " + key + " {:.3f}\t".format(concepts[key]) + '\n'
    return text

def load_nouns(segment, possible):
    for st in segment.subtrees():
        if type(st) is TreeSegmentWidget:
            if st._label._text in interest:
                possible.append(st)
            load_nouns(st, possible)

def ph(*s):
    print("hello")


global ts
if __name__ == '__main__':
    top = Tk()
    top.title("TREE!")

    top.geometry("800x500")
    parser = CoreNLP.CoreNLPParser()

    cf = CanvasFrame(width=400, height=400,parent=top)
    ts = TreeWidget(cf.canvas(), next(parser.raw_parse("What is Faculty of Electrical Engineering?")), draggable=1,
                    node_font=('helvetica', -17, 'bold'),
                    leaf_font=('helvetica', -14, 'italic'),
                    roof_fill='white', roof_color='black',
                    leaf_color='green4', node_color='blue2')

    E1 = Entry(top, bd=1,width=50,bg="white")
    E1.insert(0, "What is Faculty of Electrical Engineering?")

    cf.add_widget(ts,0,60)

    #Label for possible Concept Graph information
    ConceptText = StringVar()
    Label(top, textvariable=ConceptText, font="Courier 16 bold",justify=LEFT, bg="white").pack(side=BOTTOM)


    prevcolor = 'blue2'
    def treeClicked(smth):
        global prev,prevcolor
        prev['color'] = prevcolor
        prevcolor = smth._label.__getitem__('color')
        # tc.toggle_collapsed(smth)
        prev = smth._label
        smth._label['color'] = 'red'
        subsentence = []
        get_subsentence(smth, subsentence)

        c = _getConcept(" ".join(subsentence))
        Google(" ".join(subsentence))
        # Google(c[1])
        ConceptText.set(" ".join(subsentence) + " : " + c[1] + ("" if c[0] == 0 else ("\n" + ScoreTypes[ScoreType] + ' ' + c[0])))
        if c[1].__eq__("No concepts"):
            print(" -> " + c[1])
            return False


        print(" -> OK")
        return True

    possible = []

    def submitButton(*s):
        global ts,prev
        if E1.get() is "":
            return
        if ts.hidden():
            ts.show()


        cf.remove_widget(ts)
        ts.destroy()

        tree = next(parser.raw_parse(E1.get()))
        ts = TreeWidget(cf.canvas(), tree, draggable=1,shapeable=1,
                        node_font=('helvetica', -18, 'bold'),
                        leaf_font=('helvetica', -14, 'italic'),
                        roof_fill='white', roof_color='black',
                        leaf_color='green4', node_color='blue2')

        prev = ts._nodes[0]
        ts.bind_click_trees(treeClicked)

        cf.add_widget(ts)
        possible.clear()
        load_nouns(ts._treeseg, possible)
        print("Possible variants: ")
        for p in possible:
            p._label['color'] = 'green3'
            s = []
            get_subsentence(p, s)

            print(" - " + " ".join(s))

        for p in possible:
            if treeClicked(p):
                break

    B1 = Button(top, text='Submit', command=submitButton)

    top.bind('<Return>', lambda e: submitButton())
    top.bind('<Escape>', lambda e: top.destroy())
    top.bind('<Control-z>', lambda e: (
        ConceptText.set(""),
        E1.delete(0, 'end'),
        ts.hide(),
        print()
        ))



    top.bind('<Control-KP_0>', lambda e :(
        setScoreType(ScoreByProb),
        submitButton()
        ))

    top.bind('<Control-KP_1>', lambda e: (
        setScoreType(ScoreByCross),
        submitButton()
        ))

    E1.focus()
    E1.pack(ipady=20)
    B1.pack()
    cf.pack(side=LEFT)
    B1.invoke()

    top.mainloop()