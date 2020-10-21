from .Primitive import basicPrims
class ContextOBJ:

    # Create a new context with prims being the set of known primitives
    def __init__(self, prims=basicPrims):
        # Start with an empty file
        self.objFileText = []
        self.prims = prims
        self.vertCount = 0

    # Insert the given primitive into our object data
    # The position, size and orientation of the primitive depends on scope
    def addPrim(self, primName, scope):
        if primName not in self.prims:
            print(f"Failed to find prim with name: {primName}")
            print(f"Available prims:\n{self.prims.keys()}")
            print("Just going to use a box")
            prim = self.prims['rect']
        else:
            prim = self.prims[primName]
        # Transform the vertices into the given scope
        newVerts = scope.putVertsInScope(prim.verts, prim.boundingBox)
        # Add the new data to the object file we are building
        self.objFileText.append(f"o {primName}\n")
        self.objFileText.extend(self.vertsToObjText(newVerts))
        self.objFileText.extend(prim.otherData)
        # Add the prim's face data but make sure the faces reference the correct
        # vertices by offsetting the vertex indices
        self.objFileText.extend(self.offsetVertIndices(prim.faceData))
        self.vertCount += prim.numVerts

    # Format a list of vertices for a .obj file
    def vertsToObjText(self, vs):
        return (f"v {coords}\n" for coords in [" ".join(["%.5f" % c for c in xyz[:3]]) for xyz in vs])

    # Write the current object to a file
    def writeToFile(self, fname):
        try:
            with open(fname,"w") as f:
                f.writelines(self.objFileText)
        except:
            print(f"Failed to write to .obj file: {fname}")

    # The faces in a .obj file reference the vertex indices in a file
    # We need to offset these indices since other primitive shapes may
    # Appear before this one in the file
    def offsetVertIndices(self, faceData):
        faceLines = []
        for face in faceData:
            faceText = "f "
            for vertData in face:
                faceText += str(int(vertData[0]) + self.vertCount)
                for d in vertData[1:]:
                    faceText += f"/{d}"
                faceText += " "
            faceText+="\n"
            faceLines.append(faceText)
        return faceLines

    def reset(self):
        self.objFileText = []
        self.vertCount = 0
