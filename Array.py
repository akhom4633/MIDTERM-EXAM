# -*- coding: utf-8 -*-

import pyqtgraph as pg
import random

import time
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.parametertree.parameterTypes as pTypes
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import numpy as np

app = pg.mkQApp("Array")
win = QtGui.QWidget()
layout = QtGui.QGridLayout()
win.setLayout(layout)

table = pg.TableWidget(editable=True, sortable=True)

array_size = 10
wait_time = 100
log = ""
step_counter = 0
swap_counter = 0
compare_counter = 0
search_temp = 0

array_temp = np.array([(i) for i in range(array_size)], dtype=object)

params = [
    {'name': 'Array operation', 'type': 'group', 'children': [
        {'name': 'Array length', 'type': 'int', 'limits': (0, 100), 'value': array_size},
        {'name': 'Create Array', 'type': 'action', 'tip': 'Click me'},
        {'name': 'Random', 'type': 'action', 'tip': 'Fill array with random numbers'},
        {'name': 'Bubble sort', 'type':'action', 'tip':'Sort array with bubble sort'},
        {'name': 'wait time (ms.)', 'type': 'int', 'limits': (0, 1000), 'value': wait_time},
        {'name': 'Log', 'type': 'text', 'value': 'log ...'},
        {'name': 'search box', 'type': 'int', 'value': 0},
        {'name': 'Search', 'type': 'action', 'tip': 'Search'},
    ]},
]

## Create tree of Parameter objects
p = Parameter.create(name='params', type='group', children=params)

_sort = False
_search = False

## If anything changes in the tree, print a message
def change(param, changes):
    global array_temp, array_size, _sort,_search, wait_time, search_temp
    # print("tree changes:")
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
        if childName == "Array operation.Array length": # Specify array length
            array_size = data
        if childName == "Array operation.Create Array": # Create array
            array_temp = np.array([(i) for i in range(array_size)], dtype=object)
            pointer_array = np.array(["  "] * len(array_temp))
            table.setData(np.stack((array_temp, pointer_array), axis=1)) # update table
            win.show() # refresh UI
        if childName == 'Array operation.Random':
            temp = []
            for i in range(array_size): temp.append(random.randint(0, 100)) # random number between 0-100
            array_temp = np.asarray(temp)
            pointer_array = np.array(["  "] * len(array_temp))
            table.setData(np.stack((array_temp, pointer_array), axis=1))  # update table
            win.show()
            _sort = False # reset sort flag
        if childName == 'Array operation.Bubble sort':
            _sort = True
        if childName == 'Array operation.wait time (ms.)':
            wait_time = int(data)
        if childName == 'Array operation.search box':
            try: search_temp = int(data)
            except: print("Please enter valid data")
        if childName == 'Array operation.Search':
            _search = True
p.sigTreeStateChanged.connect(change)

pointer_array = np.array(["  "] * len(array_temp), dtype=object) # crate empty row of pointer
table.setData(np.stack((array_temp, pointer_array), axis=1)) # init table
# w.contextMenuEvent()
console = ParameterTree()
console.setParameters(p, showTop=False)
console.setWindowTitle('pyqtgraph example: Parameter Tree')
# p.child("Array operation").child("Text Parameter").setValue("log")

layout.addWidget(table, 1, 0, 1, 1)
layout.addWidget(console, 1, 1, 1, 1)
win.show()

def update():
    global table, array_size, array_temp, _sort, _search, log
    step_counter = 0
    swap_counter = 0
    compare_counter = 0
    if _search: # search flag is activated
        for i in range(array_size):
            this_log = "Move pointer to index %d\nCompare value %d with value in index %d\n" % (i, search_temp, i)
            log = this_log + log
            p.child("Array operation").child("Log").setValue(log)
            time.sleep(wait_time / 1000)
            pointer_array = np.array(["  "] * len(array_temp), dtype=object)
            pointer_array[i] = "<--"
            table.setData(np.stack((array_temp, pointer_array), axis=1))
            app.processEvents()
            compare_counter += 1
            if array_temp[i] == search_temp: # found
                this_log = "Found searched value (%d) at index %d\n" % (search_temp, i)
                log = this_log + log
                p.child("Array operation").child("Log").setValue(log)
                time.sleep(wait_time / 1000)
                break
            step_counter += 1
        this_log = "=== Move pointer count %d ===\n=== Compare count %d ===\n" % (step_counter, compare_counter)
        log = this_log + log
        p.child("Array operation").child("Log").setValue(log)

        _search = False
    if _sort: # sort flag is activated
        for i in range(array_size - 1):
            for j in range(array_size - i - 1):
                this_log = "Compare value in index %d with value in index %d\n"%(j, j+1)
                log = this_log + log
                p.child("Array operation").child("Log").setValue(log)
                time.sleep(wait_time/1000)
                compare_counter += 1
                if array_temp[j] > array_temp[j + 1]:
                    array_temp[j], array_temp[j + 1] = array_temp[j + 1], array_temp[j]  # swap
                    this_log = "Swap index %d (%d) with index %d (%d)\n"%(j, array_temp[j], j+1, array_temp[j+1])
                    log = this_log + log
                    p.child("Array operation").child("Log").setValue(log)
                    app.processEvents()
                    swap_counter += 1
                pointer_array = np.array(["  "]*len(array_temp), dtype=object)
                pointer_array[j] = "< A"
                pointer_array[j+1] = "< B"
                table.setData(np.stack((array_temp, pointer_array), axis=1))
                app.processEvents()
                this_log = "Move pointer A to index %d\nMove pointer B to index %d\n" % (j, j + 1)
                log = this_log + log
                p.child("Array operation").child("Log").setValue(log)
                step_counter += 2
        this_log = "=== Move pointer count %d ===\n=== Swap count %d ===\n=== Compare count %d ===\n" % (step_counter, swap_counter, compare_counter)
        log = this_log + log
        p.child("Array operation").child("Log").setValue(log)

        _sort = False # reset flag



timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)
if __name__ == '__main__':
    pg.exec()