# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Export Active Obj, a Blender addon
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
    "name": "Export Active Obj",
    "author": "Michel Anders (varkenvarken)",
    "version": (1, 0),
    "category": "Import-Export",
    "description": "Export selected objects as a wavefront obj file with the name of the active object",
    "blender": (4, 0, 0),
}
import bpy


def menu_func(self, context):
    self.layout.separator()
    op = self.layout.operator(
        "wm.obj_export",
        text="Export Active Obj",
    )
    op.filepath = context.active_object.name + ".obj"
    op.forward_axis = "Y"
    op.up_axis = "Z"
    op.export_selected_objects = True


def register():
    bpy.types.TOPBAR_MT_file_export.append(menu_func)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()
