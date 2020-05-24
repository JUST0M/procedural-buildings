from Visualiser import Visualiser

class VisualiserGeometry(Visualiser):

    def __init__(self, fname):
        self.fname = fname

    def visualise(self, resultGeom):

        plyFileContents = resultGeom.toPly()
        with open(self.fname, 'w') as f:
            f.write(plyFileContents)
        return(self.fname)