# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Name Match, a Blender addon
#  (c) 2024 Michel J. Anders (varkenvarken)
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Name Match",
    "author": "Michel Anders (varkenvarken)",
    "version": (1, 0),
    "category": "Object",
    "description": "Rename datablocks to match the name of the objects they are linked to",
    "blender": (4, 0, 0),
}
import bpy


class NameMatchOperator(bpy.types.Operator):
    """Rename datablocks to match the name of the objects they are linked to"""

    bl_idname = "object.name_match"
    bl_label = "Name match"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects)

    def execute(self, context):
        for obj in context.selected_objects:
            obj.data.name = obj.name
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.operator(
        NameMatchOperator.bl_idname,
        text="Rename datablocks",
        icon="PLUGIN",
    )


def register():
    bpy.utils.register_class(NameMatchOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func)
    bpy.utils.unregister_class(NameMatchOperator)


if __name__ == "__main__":
    register()
