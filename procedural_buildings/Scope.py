from .parsing.Rule import Size
from math import ceil
import numpy as np

class Scope:
    axisVector = [np.array([1,0,0]),
                  np.array([0,1,0]),
                  np.array([0,0,1])]

    # Create a new scope using the given position, rotation and size
    def __init__(self, pos, rotMat, size):
        self.pos = pos
        self.rotMat = rotMat
        self.size = size
        self.mat = None

    # Resize a paricular axis of this scope. Return the result as a new scope
    def resizeAxis(self, axis, newSize):
        if axis==0:
            newSize = np.array([newSize, self.size[1], self.size[2]])
        elif axis==1:
            newSize = np.array([self.size[0], newSize, self.size[2]])
        elif axis==2:
            newSize = np.array([self.size[0], self.size[1], newSize])
        else:
            raise RuntimeError(f'Invalid axis \'{axis}\' used in scope scale')
        return Scope(self.pos, self.rotMat, newSize)

    # Return a new scope with the given size
    def resize(self, newSize):
        size = [s.size*t if s.isRelative else s.size for (s,t) in zip(newSize,self.size)]
        return Scope(self.pos, self.rotMat, np.array(size))

    # Return a new scope representing the translation of this scope by the given vector
    def translate(self, v):
        rotV = self.rotMat.dot(v)
        return Scope(rotV + self.pos, self.rotMat, self.size)

    # Return a new scope equivalent to this scope rotated around axis by th radians
    def rotate(self, axis, th):
        c = np.cos(th)
        s = np.sin(th)
        if axis == 0:
            rot = np.array([[ 1,  0,  0],
                            [ 0,  c, -s],
                            [ 0,  s,  c]])
        elif axis == 1:
            rot = np.array([[ c,  0,  s],
                            [ 0,  1,  0],
                            [-s,  0,  c]])
        elif axis == 2:
            rot = np.array([[ c, -s,  0],
                            [ s,  c,  0],
                            [ 0,  0,  1]])
        else:
            raise RuntimeError(f'Invalid axis \'{axis}\' used in scope rotate')

        rotMat = self.rotMat.dot(rot)
        return Scope(self.pos, rotMat, self.size)

    # Create a new scope with the given position and size
    # The rotation on each axis of this new scope is 0
    def freshScope(pos, size):
        I3 = np.array([[1,0,0],
                       [0,1,0],
                       [0,0,1]])
        return Scope(pos, I3, size)

    # Split the current scope along axis it sections with sizes given by
    # splitSizes. Returns a list of scopes representing each split section.
    def split(self, axis, splitSizes):
        newScopes = []
        axisVector = self.axisVector[axis]
        unchangedSizes = self.size * (1-axisVector)
        offset = np.array([0,0,0])
        # Calculate the scale factor for any relative sizes
        scale = self.calcScale(axis, splitSizes)

        for s in splitSizes:
            # Scale if it's a relative size
            actualSize = s.size * scale if s.isRelative else s.size
            actualSizeVec = actualSize * axisVector
            sizeVec = actualSizeVec + unchangedSizes
            tVec = self.rotMat.dot(offset)
            # Create a new scope for this split section
            newScopes.append(Scope(self.pos + tVec, self.rotMat, sizeVec))
            offset = offset + actualSizeVec
        return newScopes

    # Split the scope in given direction in to n equal-sized scopes
    # where n = ceil(self.size[axis] / size)
    def repeat(self, axis, size):
        numRepeats = ceil(self.size[axis] / size)
        return self.repeatN(axis, numRepeats)

    # Split this scope along axis into n equally sizes scopes
    def repeatN(self, axis, n):
        # just split with n split sections each of relative size 1
        return self.split(axis, [Size(1,True)] * n)

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
        scopeMinusAbsolute = self.size[axis]
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

    # Return a matrix representing the transformation required to go from
    # an origin-centered 1x1x1 cube to this scope
    def toMat(self):

        scaleReCentreTranslate = np.array([[self.size[0], 0, 0, self.pos[0] + self.size[0]/2],
                                           [0, self.size[1], 0, self.pos[1] + self.size[1]/2],
                                           [0, 0, self.size[2], self.pos[2] + self.size[2]/2],
                                           [0, 0, 0, 1]])

        r = self.rotMat
        rotate = np.array([[r[0][0], r[0][1], r[0][2], 0],
                           [r[1][0], r[1][1], r[1][2], 0],
                           [r[2][0], r[2][1], r[2][2], 0],
                           [0, 0, 0, 1]])

        return np.matmul(scaleReCentreTranslate, rotate)

    # Given a list of vertices, return a list where each vertex has been
    # moved to the scope defined by self
    def putVertsInScope(self, verts, boundingBox):
        transMat = np.matmul(self.toMat(), boundingBox.matToUnitSquare())
        return np.matmul(verts, transMat.swapaxes(0,1))
