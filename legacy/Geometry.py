import numpy as np
import re

class Geom:

    # A geom consists of:
    #  - a list of verts, each of which is a vector position
    #  - a list of colours such that vert[i] has colour colour[i]
    #  - a list of faces, where a face is a list of the indices
    #    in verts of the verts that make up the face
    #  - a size
    def __init__(self, verts, colours, faces, size):

        self.verts = verts
        self.colours = colours
        self.numVerts = len(verts)
        self.faces = faces
        self.numFaces = len(faces)
        self.size = size

    # Return a ply format string
    def toPly(self):
        header = f"ply\nformat ascii 1.0\nelement vertex {self.numVerts}\nproperty float x\nproperty float y\nproperty float z\nproperty float red\nproperty float green\nproperty float blue\nelement face {self.numFaces}\nproperty list uchar uint vertex_indices\nend_header\n"
        #s = header
        lines = [header]
        for i in range(self.numVerts):
            v = self.verts[i]
            c = self.colours[i]
            #s += f'{v[0]} {v[1]} {v[2]} {c[0]} {c[1]} {c[2]}\n'
            lines.append(f'{v[0]} {v[1]} {v[2]} {c[0]} {c[1]} {c[2]}\n')
        for f in self.faces:
            #s += str(len(f))
            vs = ' '.join(map(str, f))
            lines.append(f'{len(f)} {vs}\n')
            #for v in f:
            #    s += f' {v}'
            #s += '\n'
        return ''.join(lines)

    # Given a .ply file, return a new Geom object representing the object in the file
    def fromPly(fname):
        with open(fname) as f:
            ply = f.read()
        head, body = ply.split('header')
        numVerts = int(re.search('element vertex (\d*)\n', head).group(1))
        body = body.split('\n')[1:]
        verts = []
        colours = []
        faces = []
        i = 0
        maxX, maxY, maxZ = 0, 0, 0
        while i < numVerts:
            x,y,z,*col = [float(x) for x in body[i].split(' ')]
            maxX, maxY, maxZ = max(maxX, x), max(maxY, y), max(maxZ, z)
            verts.append([x,y,z,1])
            colours.append(col)
            i += 1

        while i < len(body):
            faces.append([int(x) for x in body[i].split(' ')[1:]])
            i += 1

        return Geom(np.array(verts), colours, faces, (maxX, maxY, maxZ))

    # Take this Geom from 'scope' to the global scope by transforming vertices
    def putInGlobalScope(self, scope, colour=None):

        scaleToUnitCube = np.array([[1/self.size[0], 0, 0, 0],
                                    [0, 1/self.size[1], 0, 0],
                                    [0, 0, 1/self.size[2], 0],
                                    [0, 0, 0, 1]])
        transformationMat = scope.toMat().dot(scaleToUnitCube)
        newVerts = np.matmul(self.verts, transformationMat.swapaxes(0,1))

        if colour:
            colours = [colour] * self.numVerts
        else:
            colours = self.colours
        # TODO: fix size
        return(Geom(newVerts, colours, self.faces, [0,0,0]))

    # Add this Geom to another Geom and return the result as a new Geom
    def addGeom(self, other):
        newVerts = np.concatenate((self.verts, other.verts))
        n = self.numVerts
        newFaces = [f for f in self.faces] + [[i+n for i in f] for f in other.faces]
        newColours = [col for col in self.colours] + [col for col in other.colours]
        # TODO: fix size
        size = [0,0,0]
        return Geom(newVerts, newColours, newFaces, size)

    def __add__(self, other):
        if type(other) != Geom:
            raise TypeError(f'Can not add {other} of type {type(other)} to geom')
        else:
            return self.addGeom(other)
