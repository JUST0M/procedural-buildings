#from context import Context
import bmesh


#class ContextBlender(Context):
class ContextBlender():

    objStack = []

    # Takes a Blender context
    def __init__(self, bContext):
        self.bContext = bContext

    # Get initial object to apply the first rule to
    def getStartObj(self):
        return self.bContext.scene.objects.active

    # Push the current context onto a memory stack
    def pushObj(self, obj):
        self.objStack.append(obj)

    # Modify this context to become the one at the top of the stack
    def popObj(self, obj):
        return self.objStack.pop()

    # Split context in half in x-direction
    def split(self, obj):
        # For now just split in half and apply left and right to the new scopes
        mesh = obj.data
        print(mesh)
        bm = bmesh.from_edit_mesh(mesh)
        print(bm)# select all faces
        for f in bm.faces:
            f.select = True

        edges = [e for e in bm.edges]
        faces = [f for f in bm.faces]
        geom = []
        geom.extend(edges)
        geom.extend(faces)

        result = bmesh.ops.bisect_plane(bm,
                                        dist=0.01,
                                        geom=geom,
                                        plane_co=(0, 0, 0),
                                        plane_no=(1, 0, 0))
        print(result)
        bmesh.update_edit_mesh(mesh)
        bm.free()
        mesh.update()
        # Create new objects for each half

        # Return those

    # Colour current context
    def colour(self, obj, colour):
        mat = bpy.data.materials.new(name="MaterialName") #set new material to variable

        # Assign it to object
        if obj.data.materials:
            # assign to 1st material slot
            obj.data.materials[0] = mat
        else:
            # no slots
            obj.data.materials.append(mat)
        if colour == "red":
            mat.diffuse_color = (1, 0, 0, 1)
        elif colour == "green":
            mat.diffuse_color = (0, 1, 0, 1)
        elif colour == "blue":
            mat.diffuse_color = (0, 0, 1, 1)
        else:
            mat.diffuse_color = (1, 1, 1, 1)
