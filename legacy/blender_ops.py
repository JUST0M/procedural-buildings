import bpy
import bmesh

class Split(bpy.types.Operator):
    """My Object Splitting Script"""     # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.split_half_x"    # Unique identifier for buttons and menu items to reference.
    bl_label = "Split in half on x-axis" # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}    # Enable undo for the operator.

    def execute(self, context):          # execute() is called when running the operator.
        bpy.ops.object.mode_set(mode='EDIT')
        context = bpy.context
        ob = context.object
        mesh = ob.data
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

        return {'FINISHED'}              # Lets Blender know the operator finished successfully.

# split should be in its own thing and then just have an addon file that registers everything.
# Maybe split etc. don't even need to be registered ops