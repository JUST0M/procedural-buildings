
bl_info = {
    "name": "Run CGA Grammar",
    "category": "Object",
    "location": "View3D > Tool Shelf",
    "blender": (2, 80, 0),
}

import bpy
#import bmesh
#import blender_ops

class RunGrammar(bpy.types.Operator):
    """Run CGA Grammar"""     # Use this as a tooltip for menu items and buttons.
    bl_idname = "object.run_cga_grammar"    # Unique identifier for buttons and menu items to reference.
    bl_label = "Run CGA Grammar" # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}    # Enable undo for the operator.
    fName: bpy.props.IntProperty(name="fName", default=0)


    def execute(self, context):          # execute() is called when running the operator.
        bpy.ops.object.mode_set(mode='EDIT')
        context = bpy.context
        print(self.fName)


        return {'FINISHED'}              # Lets Blender know the operator finished successfully.

# Panel for tool
class GrammarPanel(bpy.types.Panel):
    bl_idname = "GrammarPanel"
    bl_label = "Grammar Panel"
    bl_category = "Run CGA Grammar"
    # TODO: change to object or something
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"



    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "fName")
        row = layout.row()
        row.operator('object.run_cga_grammar', text='Run CGA Grammar')


classes = (RunGrammar, GrammarPanel)

def register

register, unregister = bpy.utils.register_classes_factory(classes)

# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()
