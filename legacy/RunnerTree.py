from Runner import Runner

class RunnerTree(Runner):

    primitives = {}

    def getPrim(self, prim):
        if prim not in self.primitives:
            try:
                self.primitives[prim] = Geom.fromPly(f'primitives/{prim}.ply')
            except:
                raise RuntimeError(f'Unable to open primitive object {prim}')
        return self.primitives[prim]

    def initObj(self):
        self.obj = None

    def split(self, axis, sizes):
        return(

    def repeat(self, axis, size):
        return(self.currScope.repeat(axis, size))

    def comp(self, faces):
        return([self.currScope.comp(face) for face in faces])

    def colour(self, colour):
        colouredGeom = self.getPrim('rect').putInGlobalScope(self.currScope, colour)
        self.obj = self.obj + colouredGeom

    def rotate(self, axis, angle):
        self.currScope = self.currScope.rotate(axis, angle)

    def resizeScope(self, sx, sy, sz):
        self.currScope = self.currScope.resize(np.array([sx, sy, sz]))

    def translate(self, v):
        self.currScope = self.currScope.translate(np.array([v[0], v[1], v[2]]))

    def primitive(self, prim):
        primInScope = self.getPrim(prim).putInGlobalScope(self.currScope)
        self.obj = self.obj + primInScope