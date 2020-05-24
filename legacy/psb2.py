
bl_info = {
    "name": "Run CGA Grammar",
    "description": "",
    "author": "JUSTOM",
    "version": (0, 0, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Tool Shelf",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class PsbProperties(PropertyGroup):
    fName: StringProperty(
        name = "File",
        description="Choose a file:",
        default="",
        subtype='FILE_PATH'
        )
"""
    my_enum: EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[ ('OP1', "Option 1", ""),
                ('OP2', "Option 2", ""),
                ('OP3', "Option 3", ""),
               ]
        )
"""
# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class RunGrammar(Operator):
    """Run Grammar"""
    bl_idname = "object.run_cga_grammar"
    bl_label = "Run Grammar"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        scene = context.scene
        psbTool = scene.psb_tool

        #context = bpy.context
        print(psbTool.fName)


        return {'FINISHED'}              # Lets Blender know the operator finished successfully.

# ------------------------------------------------------------------------
#    Menus
# ------------------------------------------------------------------------
"""
class OBJECT_MT_CustomMenu(bpy.types.Menu):
    bl_label = "Select"
    bl_idname = "OBJECT_MT_custom_menu"

    def draw(self, context):
        layout = self.layout

        # Built-in operators
        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")
"""
# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class PsbPanel(Panel):
    bl_label = "PSB Panel"
    bl_idname = "PsbPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        psbTool = scene.psb_tool

        layout.prop(psbTool, "fName")
        layout.operator("object.run_cga_grammar")
"""
class OBJECT_PT_CustomPanel(Panel):
    bl_label = "My Panel"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        psbTool = scene.psb_tool

        layout.prop(psbTool, "my_bool")
        layout.prop(psbTool, "my_enum", text="")
        layout.prop(psbTool, "my_int")
        layout.prop(psbTool, "my_float")
        layout.prop(psbTool, "my_float_vector", text="")
        layout.prop(psbTool, "my_string")
        layout.prop(psbTool, "my_path")
        layout.operator("wm.hello_world")
        layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        layout.separator()
"""
# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    PsbProperties,
    RunGrammar,
    #OBJECT_MT_CustomMenu,
    PsbPanel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.psb_tool = PointerProperty(type=PsbProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.psb_tool


if __name__ == "__main__":
    register()