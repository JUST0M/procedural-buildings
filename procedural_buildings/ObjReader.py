from .Ops import OpPrimitive, OpNil, Op, OpSplit
from .BoxSplitter import Box, Container, boxesToOp
from .parsing.Rule import Size
from .Primitive import Primitive, basicPrims

# Given an object file name, create an operation graph representing the object
def objToOpGraph(fname, primDict=basicPrims.copy()):
    with open(fname) as f:
        objText = f.read()
    splitData = objText.split('o ')[1:]
    boxes = []
    # Initialise the container that bounds all primtive-bounding boxes
    container = Container(0)
    for primData in splitData:
        lines = primData.split('\n')
        primName = lines[0]
        firstCoords = [round(float(c), 6) for c in lines[1].split(' ')[1:4]]
        minCoords = firstCoords
        maxCoords = firstCoords
        i = 2
        while lines[i][0:2] == 'v ':
            coords = [round(float(c), 6) for c in lines[i].split(' ')[1:4]]
            minCoords = [min(a,b) for a,b in zip(minCoords, coords)]
            maxCoords = [max(a,b) for a,b in zip(maxCoords, coords)]
            i+=1

        # If we haven't seen this primitive object before then save it
        if primName not in primDict:
            lines[0] = f'o {primName}'
            p = Primitive(lines)
            primDict[primName] = p

        # Create a bounding box for the primitive object
        box = Box([[a,b] for (a,b) in zip(minCoords, maxCoords)], primName)
        boxes.append(box)
        # Add the box to the box-bounding container
        container.addBox(box)

    # Convert the primitive-containing boxes into an operation
    return boxesToOp(boxes, container)

# Given a list of example objects, create an operation graph representing them
def objsToOpGraph(fnames):
    primDict = basicPrims.copy()
    return Op.combineMany([objToOpGraph(f, primDict) for f in fnames]), primDict
