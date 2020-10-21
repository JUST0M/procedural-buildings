import numpy as np
from .BoxSplitter import Box

import os

class Primitive:

    # Given the lines of an object file that correspond to this primitive object,
    # create a new Primtive object that represents the object described in those lines
    def __init__(self, lines):
        i = 0
        while i < len(lines) and (len(lines[i]) < 2 or lines[i][0:2] != "o "):
            i+=1
        if i == len(lines):
            raise RuntimeError("Invalid primitive data")

        self.name = lines[i][2:]
        verts = []
        i += 1
        startOfVerts = i
        firstCoords = [round(float(c), 6) for c in lines[i].split(' ')[1:4]]
        minCoords = firstCoords[:]
        maxCoords = firstCoords[:]
        # Read the vertex data in the .obj file
        while lines[i][0:2] == 'v ':
            coords = [round(float(c), 6) for c in lines[i].split(' ')[1:4]]
            coords.append(1)
            for j in range(3):
                if coords[j] < minCoords[j]:
                    minCoords[j] = coords[j]
                if coords[j] > maxCoords[j]:
                    maxCoords[j] = coords[j]
            verts.append(coords)
            i += 1
        self.numVerts = i-startOfVerts
        # Save any other data in the file about the primitive object
        self.otherData = []
        while lines[i][0:2] != 'f ':
            self.otherData.append(lines[i] + "\n")
            i += 1
        self.faceData = []
        # Save the face data later so we know which faces use which vertices
        # we can modify these vertex indices later when the primitive object
        # appears in a different place within the .obj file
        while i<len(lines) and (lines[i][0:2] == 's ' or lines[i][0:2] == 'f '):
            if lines[i][0:2] == 'f ':
                if lines[i][-1] == " ":
                    lines[i] = lines[i][:-1]
                self.faceData.append([d.split('/') for d in lines[i].split(' ')][1:])
            i += 1
        self.otherData.extend([l+"\n" for l in lines[i:]])
        self.verts = np.array(verts)
        self.boundingBox = Box(zip(minCoords, maxCoords), self.name)

# Given a file containing only one object,
# create a new Primitive object from this object
def primFromFile(fname):
    with open(fname) as f:
        objFileLines = f.read().splitlines()
    return Primitive(objFileLines)

# basicPrims stores all primitive objects found in the primitive directory
basicPrims = {}
primDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "primitives")
for file in os.listdir(primDir):
    if file.endswith(".obj"):
        basicPrims[os.path.splitext(file)[0]] = primFromFile(os.path.join(primDir, file))
