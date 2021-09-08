# -*- coding: utf-8 -*-
import pyqtgraph as pg
import random

import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import math
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

_depth = 1
_pos = None
_pos_temp = []
_adj = None
_adj_temp = []
_symbols = []
_symbols_temp = []
_lines = []
_texts = []
_texts_temp = []
_highlight = []
_root = None

_a = 0.5 # horizontal space
_b = 1 # vertical space

_display_wait = False

app = pg.mkQApp("List")
win = QtGui.QWidget()
layout = QtGui.QGridLayout()
win.setLayout(layout)

class Node:
    # Constructor to create a new node
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
def find_depth(root, depth):
    global _depth
    if root is not None:
        find_depth(root.left, depth+1)
        find_depth(root.right, depth+1)
    else:
        if depth > _depth: _depth = depth # update maximum depth of tree
def tree2pos(root:Node, pos:list, depth):
    global _depth, _pos_temp, _a, _b, _adj_temp, _symbols_temp, _lines, _texts_temp, _highlight
    _pos_temp.append(pos) # append this node position
    if root in _highlight: _symbols_temp.append("t")# if this node needed to be highlighted
    else: _symbols_temp.append("o") # normal nodes are circle
    _texts_temp.append(str(root.key))
    delta = (2**_depth)*_a/(2**depth) # delta x of children
    this_node_index = len(_pos_temp)-1
    if root.left is not None:
        _adj_temp.append([this_node_index, len(_pos_temp)]) # connect this node to left children
        left_pos = pos.copy()
        left_pos[0] -= delta # move to left
        left_pos[1] -= _b # move below
        tree2pos(root.left, left_pos, depth+1) # recursive to left children
    if root.right is not None:
        _adj_temp.append([this_node_index, len(_pos_temp)]) # connect this node to right children
        right_pos = pos.copy()
        right_pos[0] += delta # move to right
        right_pos[1] -= _b # move below
        tree2pos(root.right, right_pos, depth+1) # recursive to right children
def update_line():
    global _lines, _adj
    _lines = np.array([(255, 255, 255, 255, 4) for i in range(len(_adj))], dtype=np.ubyte)
def insert(node, key): # A utility function to insert a new node with given key in BST
    if node is None: # If the tree is empty, return a new node
        add_log("This node is empty -> create new node")
        return Node(key)
    # Otherwise recur down the tree
    if key < node.key:
        add_log("New Key (%d) is less than key of this node (%d) -> go to left child node"%(key, node.key))
        node.left = insert(node.left, key)
    else:
        add_log("New Key (%d) is more than key of this node (%d) -> go to right child node"%(key, node.key))
        node.right = insert(node.right, key)
    return node # return the (unchanged) node pointer
def searchNode(root:Node, key:int): # return node that store searched value (return None if not found)
    global _display_wait
    ### display part ###
    if root is not None:
        _highlight = [root] # highlight this node
        _display_wait = True
        # while _display_wait: pass # wait until display updated
    ### main part ###
    if root is None or root.key == key: return root # end of leaf
    if root.key < key: # key is greater than root's key -> go to right node
        add_log("Searched key is greater than root's key -> go to right child node")
        return searchNode(root.right, key)
    else:
        add_log("Searched key is smaller than root's key -> go to left child node")
        return searchNode(root.left, key) # key is smaller than root's key -> go to left node
def deleteNode(root, key): # Given a binary search tree and a key, this function delete the key and returns the new root
    # Base Case
    if root is None: return root
    if key < root.key: # Recursive calls for ancestors of node to be deleted
        root.left = deleteNode(root.left, key)
        return root
    elif (key > root.key):
        root.right = deleteNode(root.right, key)
        return root
    # We reach here when root is the node
    # to be deleted.
    add_log("Reach node that need to be deleted " + str(root))
    # If root node is a leaf node
    if root.left is None and root.right is None:
        add_log("Deleted node is leaf node -> nothing to be done")
        return None
    # If one of the children is empty
    if root.left is None:
        add_log("Deleted node has only right child -> overwrite deleted node with right child node")
        temp = root.right
        root = None
        return temp
    elif root.right is None:
        add_log("Deleted node has only left child -> overwrite deleted node with left child node")
        temp = root.left
        root = None
        return temp
    # If both children exist
    add_log("Deleted node has 2 children -> overwrite deleted node with right child then overwrite original right node with left node until there were no left child")
    succParent = root
    # Find Successor
    succ = root.right
    while succ.left != None:
        succParent = succ
        succ = succ.left

    # Delete successor.Since successor is always left child of its parent we can safely make successor's right
    # right child as left of its parent. If there is no succ, then assign succ->right to succParent->right
    if succParent != root: succParent.left = succ.right
    else: succParent.right = succ.right
    # Copy Successor Data to root
    root.key = succ.key
    return root

_add = False
_add_value = 0
_delete = False
_delete_value = 0
_search = False
_value2search = 0
_wait_time = 100
log = ""

def add_log(string):
    global p, log
    log = string + "\n" + log
    p.child("Tree").child("Log").setValue(log)

params = [
    {'name': 'Tree', 'type': 'group', 'children': [
        {'name': 'wait time (ms.)', 'type': 'int', 'limits': (0, 1000), 'value': _wait_time},
        {'name': 'Log', 'type': 'text', 'value': 'log ...'},
        {'name': 'Search', 'type': 'group', 'children': [
            {'name': 'value', 'type': 'int', 'value': _value2search},
            {'name': 'Search', 'type': 'action', 'tip': 'Search'},
        ]},
        {'name': 'Add', 'type': 'group', 'children':[
            {'name': 'value', 'type': 'int', 'value': _add_value},
            {'name': 'Insert', 'type': 'action', 'tip': 'Insert new node at specify index'},
        ]},
        {'name': 'Delete', 'type': 'group', 'children':[
            {'name': 'value', 'type': 'int', 'value': _delete_value},
            {'name': 'Delete', 'type': 'action', 'tip': 'Pop existing node at specify index'},
        ]},
    ]},
]

## Create tree of Parameter objects
p = Parameter.create(name='params', type='group', children=params)

console = ParameterTree()
console.setParameters(p, showTop=False)
console.setWindowTitle('Tree Control')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

w = pg.GraphicsLayoutWidget(show=True)
w.setWindowTitle('Binary Tree')
v = w.addViewBox()
v.setAspectLocked()

layout.addWidget(w, 1, 0, 1, 1)
layout.addWidget(console, 1, 1, 1, 1)
win.show()

class Graph(pg.GraphItem):
    def __init__(self):
        self.dragPoint = None
        self.dragOffset = None
        self.textItems = []
        pg.GraphItem.__init__(self)
        self.scatter.sigClicked.connect(self.clicked)

    def setData(self, **kwds):
        self.text = kwds.pop('text', [])
        self.data = kwds
        if 'pos' in self.data:
            npts = self.data['pos'].shape[0]
            self.data['data'] = np.empty(npts, dtype=[('index', int)])
            self.data['data']['index'] = np.arange(npts)
        self.setTexts(self.text)
        self.updateGraph()

    def setTexts(self, text):
        for i in self.textItems:
            i.scene().removeItem(i)
        self.textItems = []
        for t in text:
            item = pg.TextItem(t)
            self.textItems.append(item)
            item.setParentItem(self)

    def updateGraph(self):
        pg.GraphItem.setData(self, **self.data)
        for i, item in enumerate(self.textItems):
            item.setPos(*self.data['pos'][i])

    def mouseDragEvent(self, ev):
        if ev.button() != QtCore.Qt.MouseButton.LeftButton:
            ev.ignore()
            return

        if ev.isStart():
            # We are already one step into the drag.
            # Find the point(s) at the mouse cursor when the button was first
            # pressed:
            pos = ev.buttonDownPos()
            pts = self.scatter.pointsAt(pos)
            if len(pts) == 0:
                ev.ignore()
                return
            self.dragPoint = pts[0]
            ind = pts[0].data()[0]
            self.dragOffset = self.data['pos'][ind] - pos
        elif ev.isFinish():
            self.dragPoint = None
            return
        else:
            if self.dragPoint is None:
                ev.ignore()
                return

        ind = self.dragPoint.data()[0]
        self.data['pos'][ind] = ev.pos() + self.dragOffset
        self.updateGraph()
        ev.accept()

    def clicked(self, pts):
        print("clicked: %s" % pts)

g = Graph()
v.addItem(g)

def change(param, changes):
    global _search, _value2search, _add, _add_value, _delete, _delete_value, _wait_time
    for param, change, data in changes:
        path = p.childPath(param)
        if path is not None:
            childName = '.'.join(path)
        else:
            childName = param.name()
        # print('  parameter: %s' % childName)
        # print('  change:    %s' % change)
        # print('  data:      %s' % str(data))
        # print('  ----------')
        if childName == "Tree.Search.Search":
            _search = True
        if childName == "Tree.Search.value":
            _value2search = int(data)
        if childName == "Tree.Add.Insert":
            _add = True
        if childName == "Tree.Add.value":
            _add_value = int(data)
        if childName == "Tree.Delete.Delete":
            _delete = True
        if childName == "Tree.Delete.value":
            _delete_value = int(data)
        if childName == "Tree.wait time (ms.)":
            _wait_time = int(data)
p.sigTreeStateChanged.connect(change)

def update(): # update of action
    global _add, _add_value, _delete, _delete_value, _search, _value2search
    global _root, _pos, _adj, _symbols, _texts, _depth
    global _pos_temp, _adj_temp, _symbols_temp, _texts_temp
    if _add:
        _root = insert(_root, _add_value)
        _add = False
    if _delete:
        _root = deleteNode(_root, _delete_value)
        _delete = False
    if _search:
        node = searchNode(_root, _value2search)
        if node is None: add_log("Value %d not found in this tree"%(_value2search))
        else: add_log("Value %d founded in Node"%(_value2search) + str(node))
        _search = False

def display_update(): # update of display & animation
    global _add, _add_value, _delete, _delete_value, _search, _value2search
    global _root, _pos, _adj, _symbols, _texts, _depth
    global _pos_temp, _adj_temp, _symbols_temp, _texts_temp
    global _display_wait
    if _root is not None:
        if _display_wait: # display process with wait time
            print("AAA")
            find_depth(_root, 0)
            _pos_temp = []  # clear pos temp
            _adj_temp = []  # clear adj temp
            _symbols_temp = []  # clear symbol temp
            _texts_temp = []  # clear text temp
            tree2pos(_root, [0, 0], 0)
            _pos = np.array(_pos_temp)
            _adj = np.array(_adj_temp)
            _symbols = _symbols_temp
            _texts = _texts_temp
            update_line()

            g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
            app.processEvents()  # update GUI
            time.sleep(_wait_time/1000)
            _display_wait = False
        ### Normal Display loop ###
        find_depth(_root, 0)
        _pos_temp = []  # clear pos temp
        _adj_temp = []  # clear adj temp
        _symbols_temp = []  # clear symbol temp
        _texts_temp = []  # clear text temp
        tree2pos(_root, [0, 0], 0)
        _pos = np.array(_pos_temp)
        _adj = np.array(_adj_temp)
        _symbols = _symbols_temp
        _texts = _texts_temp
        update_line()

        g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
        app.processEvents()  # update GUI

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)

timer1 = QtCore.QTimer()
timer1.timeout.connect(display_update)
timer1.start(0)

if __name__ == '__main__':
    ## init tree ##
    #               50
    #            /     \
    #           30      70
    #          /  \    /  \
    #        20   40  60   80 """
    _root = insert(_root, 50)
    _root = insert(_root, 30)
    _root = insert(_root, 20)
    _root = insert(_root, 40)
    _root = insert(_root, 70)
    _root = insert(_root, 60)
    _root = insert(_root, 80)
    pg.exec()