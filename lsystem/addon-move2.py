import bpy

class Move2Operator(bpy.types.Operator):
    """Move2 Operator"""
    bl_idname = "object.move2_operator"
    bl_label = "Move2 Operator"

    def execute(self, context):
        return {'FINISHED'}

def add_object_button(self, context):
    self.layout.operator(
        Move2Operator.bl_idname,
        text=Move2Operator.__doc__,
        icon='PLUGIN')

def register():
    bpy.utils.register_class(Move2Operator)
    bpy.types.VIEW3D_MT_object.append(add_object_button)

if __name__ == "__main__":
    register()