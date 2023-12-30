# ##### BEGIN GPL LICENSE BLOCK #####
#
#  facemap_select, (c) 2023 Michel Anders (varkenvarken)
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

# we cannot select faces from a defined facemap (yet), see
# https://projects.blender.org/blender/blender/issues/105317
# therefore I created this tine add-on.
# It adds two options to the Select menu in mesh edit mode:
# From facemap and Create facemap.

bl_info = {
    "name": "FacemapSelect",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20231014152157),
    "blender": (4, 0, 0),
    "location": "Edit mode 3d-view, Select- -> From facemap | Create facemap",
    "description": "Select faces based on the active boolean facemap or create a new facemap",
    "warning": "",
    "wiki_url": "https://github.com/varkenvarken/blenderaddons",
    "category": "Mesh",
}


import bpy

class FacemapSelect(bpy.types.Operator):
    bl_idname = "mesh.facemap_select"
    bl_label = "FacemapSelect"
    bl_description = "Select faces based on active facemap"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return (
            context.mode == "EDIT_MESH"
            and context.active_object.type == "MESH"
            and context.active_object.data.attributes.active is not None
            and context.active_object.data.attributes.active.domain == "FACE"
            and context.active_object.data.attributes.active.data_type == "BOOLEAN"
        )

    def execute(self, context):
        if not self.__shift:
            bpy.ops.mesh.select_all(action="DESELECT")
        attribute_name = context.active_object.data.attributes.active.name
        bpy.ops.object.editmode_toggle()
        for polygon, facemap_attribute in zip(
            context.active_object.data.polygons,
            context.active_object.data.attributes[attribute_name].data,
        ):
            polygon.select = facemap_attribute.value
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}
    
    def invoke(self, context, event):
        self.__shift = event.shift
        return self.execute(context)

class FacemapCreate(bpy.types.Operator):
    bl_idname = "mesh.facemap_create"
    bl_label = "FacemapCreate"
    bl_description = "Create a new boolean face map and set value according to current selection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_MESH" and context.active_object.type == "MESH"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        facemap = context.active_object.data.attributes.new(
            name="Facemap", domain="FACE", type="BOOLEAN"
        )
        for polygon in context.active_object.data.polygons:
            facemap.data[polygon.index].value = polygon.select
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(FacemapSelect.bl_idname, text="From facemap")
    self.layout.operator(FacemapCreate.bl_idname, text="Create facemap")


def register():
    bpy.utils.register_class(FacemapSelect)
    bpy.utils.register_class(FacemapCreate)
    bpy.types.VIEW3D_MT_select_edit_mesh.append(menu_func)


def unregister():
    bpy.types.VIEW3D_MT_select_edit_mesh.remove(menu_func)
    bpy.utils.unregister_class(FacemapSelect)
    bpy.utils.unregister_class(FacemapCreate)


if __name__ == "__main__":
    register()
