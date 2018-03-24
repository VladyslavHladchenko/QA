from tree import draw_trees
from tree import TreeView
import nltk.parse.corenlp as CoreNLP
import tkinter
from nltk.treeprettyprinter import TreePrettyPrinter
from nltk.tree import _child_names

def printName(smth):
    print(smth.__class__.__name__)

parser = CoreNLP.CoreNLPParser()
parsed = next(parser.raw_parse("what is orange pie? why the sky is blue?"))

tkinter._test()
TreeView(parsed).mainloop()

for st in parsed.subtrees():
    print("\nChilds: " ,end="")
    print(_child_names(st))
    print("Leaves: ", end="")
    print(st.leaves())
    st.pretty_print()




