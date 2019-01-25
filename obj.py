#!/usr/bin/env python3
from collections import OrderedDict
from itertools import zip_longest
from functools import reduce

import operator
import itertools
import datetime
import json
import shutil
import os
import datetime

class Obj:
    def __init__(self):
        self.rawdata = OrderedDict()
        self._workingdir = None

    def nodes(self):
        return self._getEntries('nodes').items()

    def verticies(self):
        return self._getEntries('verticies')

    def vertexNormals(self):
        return self._getEntries('vertexNormals')

    def vertexTextures(self):
        return self._getEntries('vertexTextures')

    def vertex(self, face_index):
        return self.verticies[face_index]

    def vertexNormal(self, face_index):
        return self.vertexNormals[face_index]

    def vertexTexture(self, face_index):
        return self.vertexTextures[face_index]

    def _getEntry(self, type, index):
        entries = self.rawdata.get(type, [])
        if index >= len(entries):
            return None
        return entries[index]

    def _getEntries(self, element):
        return self.rawdata[element]


def __build_model(nodes, verticies, vertexNormals, vertexTextures, path):
    model = Obj()
    model.rawdata = {'nodes': nodes,
                     'verticies': verticies,
                     'vertexNormals': vertexNormals,
                     'vertexTextures': vertexTextures
                     }
    model._workingdir = path
    return model


def parse(path):
    """
    Takes .obj filename and returns dict of object properties for each object in file.
    """
    with open(path) as f:
        lines = f.read().splitlines()
        data = f

    verts = [i.replace('v ', '') for i in lines if 'v ' in i]
    vertexNormals = [i.replace('vn ', '') for i in lines if 'vn ' in i]
    vertexTextures = [i.replace('vt ', '') for i in lines if 'vt ' in i]
    newlines = [i.split('f ')[-1] for  i in lines if i.startswith('g ') or i.startswith('f ')]
    indices = [i for i, j in enumerate(newlines) if j.startswith('g ')]

    d = {}
    for face in [newlines[i:j] for i, j in zip_longest(indices, indices[1:])]:
        d[face[0].replace('g ','' )] = {'faces':  [ [[ int(y)-1 for y in x.split('/')] for x in lst] for lst in [i.split(' ') for i in face[1:]] ]}

    obj = __build_model(d, verts, vertexNormals, vertexTextures, path)
    return obj


def _build_vertexList(indexlist, v_i , elem_list):
    i_ls = reduce(operator.concat, [[x[v_i] for x in i_ls] for i_ls in indexlist])
    i_ls = sorted(list(OrderedDict.fromkeys(i_ls)))
    ls = [elem_list[i] for i in i_ls]
    return ls


def _write_element(fileObj, elem_list, prepend):
    for f_l in elem_list:
        fileObj.write('{} {}\n'.format(prepend, ''.join(f_l)))
    fileObj.write('# {} elements\n\n'.format(len(elem_list)))


def write(model, path):
    with open(path, 'w', encoding='utf-8') as w:
        w.write('{}\n# Exported using OBJ-PYTHON-PARSER\n# File Created:{}\n{}\n\n'.format('#'*45,datetime.datetime.now(),'#'*45))
        for node_name, node in model.nodes():
            # write comment with group/object name
            w.write('#\n# object {}\n#\n\n'.format(node_name))
            #  write verticies
            _write_element(w, _build_vertexList(node['faces'], 0, model.verticies()), 'v')
            # write vertexNormals
            _write_element(w, _build_vertexList(node['faces'], 2, model.vertexNormals()), 'vn')
            # write vertexTexture
            _write_element(w, _build_vertexList(node['faces'], 1, model.vertexTextures()), 'vt')
            # write groups
            w.write('g {}\n'.format(node_name))
            # write faces
            _write_element(w, [['/'.join([str(int(i) + 1) for i in x])+ " " for x in ls] for ls in node['faces']], 'f ')
            w.write('\n\n')


def read_wavefront(infile):
    obj = parse(infile)
    return obj

