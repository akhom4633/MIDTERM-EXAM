# -*- coding: utf-8 -*-
import pyqtgraph as pg
import random

import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import math
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType

app = pg.mkQApp("List")
win = QtGui.QWidget()
layout = QtGui.QGridLayout()
win.setLayout(layout)

class Node():
    def __init__(self):
        self.previous = None
        self.next = None
        self.value = None
    def length(self):
        counter = 1
        previous_node = self
        while previous_node.next is not None:
            previous_node = previous_node.next
            counter += 1
        return counter
    def get(self, n):
        previous_node = self
        for i in range(n):
            previous_node = previous_node.next
        return previous_node
def circular_pos(n, r):
    pos = []
    for i in range(n):
        pos.append([r*math.sin(2*math.pi*i/n), r*math.cos(2*math.pi*i/n)])
    return np.array(pos)
def circular_pos_with_extend(N, n, r, d): # N=total node, n=index of extend node, r = default radius, d=extend radius
    pos = []
    for i in range(N):
        if i == n: pos.append([(r+d) * math.sin(2 * math.pi * i / n), (r+d) * math.cos(2 * math.pi * i / n)])
        else: pos.append([r * math.sin(2 * math.pi * i / n), r * math.cos(2 * math.pi * i / n)])
    return np.array(pos)
def list2adj(nodes:list, highlight = []):
    all_node = []
    adj = []
    texts = []
    for node in nodes:
        previous_node = node

        if node not in all_node: all_node.append(node)
        while previous_node.next is not None:
            previous_node = previous_node.next
            if previous_node not in all_node:
                all_node.append(previous_node)
    for node in all_node:
        texts.append(str(node.value))
        # if node.value is not None: texts.append(str(node.value))
        if node.next is not None:
            adj.append([all_node.index(node), all_node.index(node.next)])
    line = np.array([(255, 255, 255, 255, 4) for i in range(len(adj))], dtype=np.ubyte)
    symbols = ['o' for i in range(len(all_node))]
    for i in range(len(highlight)):
        symbols[highlight[i]] = "t" if i%2==0 else "+"
    return np.array(adj), line, symbols, texts
def swap(B:Node, C:Node):
    A = B.previous
    D = C.next
    if A is not None: A.next = C
    B.previous = C
    B.next = D
    C.previous = A
    C.next = B
    if D is not None: D.previous = B
def create_list(n):
    first_node = Node()
    first_node.value = 0
    previous_node = first_node
    for i in range(n - 1):
        new_node = Node()
        new_node.value = i + 1
        previous_node.next = new_node
        new_node.previous = previous_node
        previous_node = new_node
    return first_node
_list_size = 5
_add = False
_add_index = 0
_add_value = 0
_pop = 0
_pop_index = 0
_node2add = None
_sort = False
_search = False
_value2search = 0
_wait_time = 100
log = ""

_pos = circular_pos(5, 10)
_adj = np.array([[0,1], [1,2], [2,3], [3,4]])
_symbols = ['o' for i in range(_list_size)]
_lines = np.array([(255, 255, 255, 255, 4) for i in range(_list_size)], dtype=np.ubyte)
_texts = [str(i) for i in range(_list_size)]
_first_node = create_list(_list_size)

step_counter = 0


def add_log(string):
    global p, log
    log = string + "\n" + log
    p.child("List operation").child("Log").setValue(log)

params = [
    {'name': 'List operation', 'type': 'group', 'children': [
        {'name': 'List length', 'type': 'int', 'limits': (0, 100), 'value': _list_size},
        {'name': 'Create List', 'type': 'action', 'tip': 'Click me'},
        {'name': 'Random', 'type': 'action', 'tip': 'Fill array with random numbers'},
        {'name': 'Bubble sort', 'type':'action', 'tip':'Sort array with bubble sort'},
        {'name': 'wait time (ms.)', 'type': 'int', 'limits': (0, 1000), 'value': _wait_time},
        {'name': 'Log', 'type': 'text', 'value': 'log ...'},
        {'name': 'Search', 'type': 'group', 'children': [
            {'name': 'value', 'type': 'int', 'value': _value2search},
            {'name': 'Search', 'type': 'action', 'tip': 'Search'},
        ]},
        {'name': 'Add', 'type': 'group', 'children':[
            {'name': 'value', 'type': 'int', 'value': _add_value},
            {'name': 'index', 'type': 'int', 'value': _add_index},
            {'name': 'Insert', 'type': 'action', 'tip': 'Insert new node at specify index'},
        ]},
        {'name': 'Pop', 'type': 'group', 'children':[
            {'name': 'index', 'type': 'int', 'value': _pop_index},
            {'name': 'Pop', 'type': 'action', 'tip': 'Pop existing node at specify index'},
        ]},
    ]},
]

## Create tree of Parameter objects
p = Parameter.create(name='params', type='group', children=params)

console = ParameterTree()
console.setParameters(p, showTop=False)
console.setWindowTitle('List Control')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

w = pg.GraphicsLayoutWidget(show=True)
w.setWindowTitle('List')
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
    global _list_size, _search, _sort, _add, _add_index, _add_value, _pop, _pop_index, _value2search, _wait_time, _node2add, _pos, _adj, _symbols, _lines, _texts, _first_node
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
        if childName == "List operation.List length": # Specify list length
            _list_size = data
        if childName == "List operation.Create List": # Create list
            _first_node = create_list(_list_size)
            _pos = circular_pos(_list_size, 10)
            # win.show() # refresh UI
        if childName == 'List operation.Random':
            previous_node = _first_node
            while previous_node.next is not None:
                previous_node.value = random.randint(0, 100)
                previous_node = previous_node.next
            previous_node.value = random.randint(0, 100)
        if childName == 'List operation.Bubble sort':
            _sort = True
        if childName == 'List operation.wait time (ms.)':
            _wait_time = int(data)
        if childName == 'List operation.Search.value':
            try: _value2search = int(data)
            except: print("Please enter valid data")
        if childName == 'List operation.Search.Search':
            _search = True
        if childName == 'List operation.Add.value':
            try: _add_value = int(data)
            except: print("Please enter valid data")
        if childName == 'List operation.Add.index':
            try: _add_index = int(data)
            except: print("Please enter valid data")
        if childName == 'List operation.Add.Insert':
            _add = True
        if childName == 'List operation.Pop.index':
            try: _pop_index = int(data)
            except: print("Please enter valid data")
        if childName == 'List operation.Pop.Pop':
            _pop = True

p.sigTreeStateChanged.connect(change)


def update():
    global w, _pos, _adj, _lines, _symbols, _texts, _first_node, _sort, _search, _value2search, _add, _add_index, _add_value, _node2add, _pop, _pop_index, step_counter, _list_size

    if _search:
        previous_node = _first_node
        index = 0
        while previous_node.next is not None:
            if previous_node.value == _value2search:
                add_log("Found %d at index %d"%(_value2search, index))
                break
            else:
                add_log("Not Found ... Move pointer to Next Node")
                _adj, _lines, _symbols, _texts = list2adj([_first_node], [index])  # highlight node that pointer pointing at
                g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
                app.processEvents()  # update GUI
                time.sleep(_wait_time/1000)
            previous_node = previous_node.next
            index += 1
        _search = False
    if _sort:
        if _first_node.length()>1:
            for i in range(_list_size - 1):
                add_log("Move pointerA to index 0 and pointerB to index 1")
                for j in range(_list_size - i - 1):
                    add_log("Move pointerA to index %d and pointerB to index %d"%(j, j+1))
                    pointerA = _first_node.get(j)
                    pointerB = _first_node.get(j+1)
                    _adj, _lines, _symbols, _texts = list2adj([_first_node], [j, j+1]) # hightlight compare nodes
                    g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
                    app.processEvents()  # update GUI
                    time.sleep(_wait_time / 1000)
                    add_log("Compare value in index %d with value in index %d"%(j, j+1))
                    if pointerA.value > pointerB.value:
                        swap(pointerA, pointerB) # swap nodes to correct order
                        if j==0: _first_node=pointerB # update _first pointer if first node is swapped
                        add_log("Swap index %d with index %d"%(j, j+1))
                        _adj, _lines, _symbols, _texts = list2adj([_first_node], [j+1, j])  # hightlight swapped nodes
                        g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
                        app.processEvents()  # update GUI
                        time.sleep(_wait_time / 1000)

        _adj, _lines, _symbols, _texts = list2adj([_first_node], [])  # highlight node that pointer pointing at
        g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
        app.processEvents()  # update GUI
        _sort = False

    if _add:
        new_node = Node()
        new_node.value = _add_value
        # _pos = circular_pos(_first_node.length()+1, 10) # generate new position (including new node)
        _pos = circular_pos_with_extend(_first_node.length() + 1, _first_node.length(), 10, 5)
        _adj, _lines, _symbols, _texts = list2adj([_first_node, new_node], [_list_size]) # generate new adj
        g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
        app.processEvents() # update GUI
        add_log("Create new node with value %d"%(new_node.value))
        time.sleep(1)
        previous_node = _first_node
        for i in range(_add_index): # move to node that pretend to be new_node.next
            previous_node = previous_node.next # move to next node
            step_counter += 1 # move pointer
        add_log("Move pointer to index %d"%(_add_index))
        new_node.next = previous_node # point new_node to node that pretend to be new_node.next
        new_node.previous = previous_node.previous # also previous address
        add_log("Point next address of new node to node at index %d"%(_add_index))
        _adj, _lines, _symbols, _texts = list2adj([_first_node, new_node], [_list_size]) # generate new adj
        g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
        app.processEvents() # update GUI
        time.sleep(1)
        if _add_index != 0: # point back if new node is not first node
            previous_node.previous.next = new_node # point node that pretend to be new_node.previous to new_node
            add_log("Point next address of node at index %d to new node"%(_add_index-1))
        else: # if this is first node
            _first_node = new_node # set as new first node
        _pos = circular_pos(_first_node.length(), 10) # re-arrange nodes
        _adj, _lines, _symbols, _texts = list2adj([_first_node], [_add_index]) # no need to insert new_node any more
        g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
        app.processEvents() # update GUI
        time.sleep(1)
        _list_size = _first_node.length() # update list size for reference
        _add = False
    if _pop:
        add_log("Move pointer to node at index %d"%(_pop_index))
        print(_pop_index)
        if _pop_index != 0:
            _pos = circular_pos(_first_node.length(), 10)
            _adj, _lines, _symbols, _texts = list2adj([_first_node], [_pop_index])  # mark node to be deleted
            g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
            app.processEvents()  # update GUI
            time.sleep(1)
            previous_node = _first_node
            for i in range(_pop_index): # move to node that pretend to be deleted
                previous_node = previous_node.next
                step_counter += 1
            delnode = previous_node
            add_log("Point next address of previous node (index %d) to next node (index %d)"%(_pop_index-1, _pop_index+1))
            delnode.previous.next = delnode.next
            add_log("Point previous address of next node (index %d) to previous node (index %d)"%(_pop_index+1, _pop_index-1))
            delnode.next.previous = delnode.previous
            _pos = circular_pos(_first_node.length(), 10)
            _adj, _lines, _symbols, _texts = list2adj([_first_node], [])  # mark node to be deleted
            g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
            app.processEvents()  # update GUI
            time.sleep(1)
        else:
            _pos = circular_pos(_first_node.length(), 10)
            _adj, _lines, _symbols, _texts = list2adj([_first_node], [0])  # mark node to be deleted
            g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
            app.processEvents()  # update GUI
            time.sleep(1)
            add_log("Point node from next address of first node as new first node")
            _first_node = _first_node.next
            _first_node.previous = None # remove old node
            _pos = circular_pos(_first_node.length(), 10) # update pos after delete
            _adj, _lines, _symbols, _texts = list2adj([_first_node], [])  # mark node to be deleted
            g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
            app.processEvents()  # update GUI
            time.sleep(1)
        _pop = False
    _adj, _lines, _symbols, _texts = list2adj([_first_node])
    g.setData(pos=_pos, adj=_adj, pen=_lines, size=1, symbol=_symbols, pxMode=False, text=_texts)
    # time.sleep(_wait_time/1000)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)
if __name__ == '__main__':
    pg.exec()
