from Rule import Size
from math import ceil
import numpy as np

class Scope:
    axisVector = {'x': np.array([1,0,0]),
                  'y': np.array([0,1,0]),
                  'z': np.array([0,0,1])}

    def __init__(self, pos, rotMat, size):
        self.pos = pos
        self.rotMat = rotMat
        self.size = size
        self.mat = None
        self.sizeDict = {'x': size[0],
                         'y': size[1],
                         'z': size[2]}

    #def scale(self, vec):
    #    return Scope(self.coordSys, [s*v for (s,v) in zip(self.size, vec)])

    def resize(self, newSize):
        size = [s.size*t if s.isRelative else s.size for (s,t) in zip(newSize,self.size)]
        return Scope(self.pos, self.rotMat, np.array(size))

    def translate(self, v):
        rotV = self.rotMat.dot(v)
        return Scope(rotV + self.pos, self.rotMat, self.size)

    def rotate(self, axis, th):
        c = np.cos(th)
        s = np.sin(th)
        if axis == 'x':
            rot = np.array([[ 1,  0,  0],
                            [ 0,  c, -s],
                            [ 0,  s,  c]])
        elif axis == 'y':
            rot = np.array([[ c,  0,  s],
                            [ 0,  1,  0],
                            [-s,  0,  c]])
        elif axis == 'z':
            rot = np.array([[ c, -s,  0],
                            [ s,  c,  0],
                            [ 0,  0,  1]])
        else:
            raise RuntimeError(f'Invalid axis \'{axis}\' used in scope rotate')

        rotMat = self.rotMat.dot(rot)
        return Scope(self.pos, rotMat, self.size)

    def freshScope(pos, size):
        I3 = np.array([[1,0,0],
                       [0,1,0],
                       [0,0,1]])
        return Scope(pos, I3, size)

    def split(self, axis, splitSizes):
        newScopes = []
        axisVector = self.axisVector[axis]
        unchangedSizes = self.size * (1-axisVector)
        offset = np.array([0,0,0])
        scale = self.calcScale(axis, splitSizes)

        for s in splitSizes:
            actualSize = s.size * scale if s.isRelative else s.size
            actualSizeVec = actualSize * axisVector
            sizeVec = actualSizeVec + unchangedSizes
            tVec = self.rotMat.dot(offset)
            newScopes.append(Scope(self.pos + tVec, self.rotMat, sizeVec))
            offset = offset + actualSizeVec
        return newScopes

    # Split the scope in given direction in to n equal-sized scopes
    # where n = ceil(self.size[axis] / size)
    def repeat(self, axis, size):
        numRepeats = ceil(self.sizeDict[axis] / size)
        size = Size(1,True)
        # just split with numRepeats split sections each of relative size 1
        return self.split(axis, [size] * numRepeats)

    # Return a scope that is restricted to just the given face
    def comp(self, face):
        s = self.size
        # TODO: could maybe be neater with dict
        if face == 'top':
            return Scope(self.pos, self.rotMat, np.array([s[0],s[1],0])).translate(np.array([0,0,s[2]]))
        elif face == 'bottom':
            return Scope(self.pos, self.rotMat, np.array([s[0],s[1],0]))
        elif face == 'back':
            return Scope(self.pos, self.rotMat, np.array([s[0],0,s[2]])).translate(np.array([0,s[1],0]))
        elif face == 'front':
            return Scope(self.pos, self.rotMat, np.array([s[0],0,s[2]]))
        elif face == 'right':
            return Scope(self.pos, self.rotMat, np.array([0,s[1],s[2]])).translate(np.array([s[0],0,0]))
        elif face == 'left':
            return Scope(self.pos, self.rotMat, np.array([0,s[1],s[2]]))
        else:
            raise RuntimeError(f'Invalid face name {face} used in comp operation')


    # Calculate the scalar to apply to relative sizes
    def calcScale(self, axis, sizes):
        scopeMinusAbsolute = self.sizeDict[axis]
        totalRelative = 0
        for s in sizes:
            if s.isRelative:
                totalRelative += s.size
            else:
                scopeMinusAbsolute -= s.size

        # If totalRelative is zero there are no relative sizes so whatever
        # we return will not be used. So just return 1
        if totalRelative == 0:
            return 1

        return scopeMinusAbsolute / totalRelative

    def toMat(self):
        centre = np.array([[1, 0, 0, -0.5],
                           [0, 1, 0, -0.5],
                           [0, 0, 1, -0.5],
                           [0, 0, 0, 1]])

        scaleReCentreTranslate = np.array([[self.size[0], 0, 0, self.pos[0] + self.size[0]/2],
                                           [0, self.size[1], 0, self.pos[1] + self.size[1]/2],
                                           [0, 0, self.size[2], self.pos[2] + self.size[2]/2],
                                           [0, 0, 0, 1]])

        r = self.rotMat
        rotate = np.array([[r[0][0], r[0][1], r[0][2], 0],
                           [r[1][0], r[1][1], r[1][2], 0],
                           [r[2][0], r[2][1], r[2][2], 0],
                           [0, 0, 0, 1]])

        if self.mat == None:
            self.mat = np.matmul(scaleReCentreTranslate, np.matmul(rotate, centre))
        return self.mat
