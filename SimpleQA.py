import nltk.parse.corenlp as CoreNLP
import json
from urllib.request import urlopen
from urllib.parse import urlencode
from nltk.draw.util import CanvasFrame, BoxWidget, TextWidget
from nltk.draw.tree import TreeWidget, TreeSegmentWidget
from tkinter.font import Font
from tkinter import Entry, Button, Text, Tk, LEFT, RIGHT, INSERT, CURRENT
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

def _conceptsFromInstance(instance):
    apiEndpointUrl = "https://concept.research.microsoft.com/api/Concept/ScoreByProb"
    topK = 50

    params = {
        "instance": instance,
        'topK': topK
    }
    url = apiEndpointUrl + '?' + urlencode(params)
    response = json.loads(urlopen(url).read().decode('utf8'))
    return response

def _getConcept(sent):
    print("Concept request ",end="")
    print("<" + sent + ">")
    concepts = _conceptsFromInstance(sent)
    max = 0
    text = ""

    for key in concepts:
        if key.__len__() > max:
            max = key.__len__()
            text = key + " \nP(↑ concept ↑|Instance) = {:.3f}".format(concepts[key])

    if text.__eq__(""):
        text="No concepts"
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
    top = Tk(className="Tree")
    global ts
    parser = CoreNLP.CoreNLPParser()
    cf = CanvasFrame(width=900, height=300,parent=top)

    ts = TreeWidget(cf.canvas(), next(parser.raw_parse("What is Faculty of Electrical Engineering?")), draggable=1,
                    node_font=('helvetica', -17, 'bold'),
                    leaf_font=('helvetica', -14, 'italic'),
                    roof_fill='white', roof_color='black',
                    leaf_color='green4', node_color='blue2')

    E1 = Entry(top, bd=1,width=50,bg="white")
    E1.insert(0,"What is Faculty of Electrical Engineering?")
    E1.pack(ipady=20)
    E1.focus()

    instance = TextWidget(cf.canvas(), "", font=Font(family="Times New Roman", size=15))
    instancebox = BoxWidget(cf.canvas(), instance, fill='white', draggable=1)

    concept = TextWidget(cf.canvas(), "", font=Font(family="Times New Roman", size=15))
    conceptbox = BoxWidget(cf.canvas(), concept, fill='white', draggable=1)

    cf.add_widget(instancebox, 600, 50)
    cf.add_widget(conceptbox, 500, 90)
    cf.add_widget(ts)

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

        instance.set_text("Instance: " + " ".join(subsentence))
        c = _getConcept(" ".join(subsentence))

        concept.set_text(c)

        if c.__eq__("No concepts"):
            print(" -> " + c)
            return False
        print(" -> OK")
        return True

    possible = []

    def submitButton(*s):
        global ts,prev
        instance.set_text("")
        concept.set_text("")
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
    B1.pack()
    cf.pack()
    B1.invoke()

    top.mainloop()