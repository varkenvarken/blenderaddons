# ##### BEGIN GPL LICENSE BLOCK #####
#
#  facemap_select, (c) 2023 Michel Anders (varkenvarken) and contributors.
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
# therefore I created this tiny add-on.
# It adds two options to the Select menu in mesh edit mode:
# From facemap and Create facemap.

bl_info = {
    "name": "FacemapSelect",
    "author": "Michel Anders (varkenvarken) with contribution from Andrew Leichter (aleichter) and Tyo79",
    "version": (0, 0, 20241107135318),
    "blender": (4, 0, 0),
    "location": "Edit mode 3d-view, Select- -> From facemap | Create facemap",
    "description": "Select faces based on the active boolean facemap or create a new facemap",
    "warning": "",
    "wiki_url": "https://github.com/varkenvarken/blenderaddons",
    "category": "Mesh",
}

import bpy
from bpy.types import Menu, Panel, UIList
import bmesh


class FacemapSelect(bpy.types.Operator):
    bl_idname = "mesh.facemap_select"
    bl_label = "FacemapSelect"
    bl_description = (
        "Select faces based on active facemap (+ Shift add to current selection)"
    )
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
            polygon.select |= (
                facemap_attribute.value
            )  # keeps polygons selected that already were
        bpy.ops.object.editmode_toggle()
        return {"FINISHED"}

    def invoke(self, context, event):
        self.__shift = event.shift
        return self.execute(context)


class FacemapCreate(bpy.types.Operator):
    bl_idname = "mesh.facemap_create"
    bl_label = "FacemapCreate"
    bl_description = (
        "Create a new boolean face map and set value according to current selection"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_MESH" and context.active_object.type == "MESH"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        facemap = context.active_object.data.attributes.new(
            name="FaceMap", domain="FACE", type="BOOLEAN"
        )

        for polygon in context.active_object.data.polygons:
            facemap.data[polygon.index].value = polygon.select
        bpy.ops.object.editmode_toggle()

        attrs = context.object.data.attributes
        attrs.active = facemap

        return {"FINISHED"}


class FacemapAssign(bpy.types.Operator):
    bl_idname = "mesh.facemap_assign"
    bl_label = "FacemapAssign"

    param: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        fm = context.object.data.attributes.active
        return fm is not None and fm.domain == "FACE" and fm.data_type == "BOOLEAN"

    def execute(self, context):
        obj = context.object
        facemap = context.object.data.attributes.active
        attribute_name = facemap.name

        bpy.ops.object.editmode_toggle()

        if attribute_name in obj.data.attributes:
            attribute = obj.data.attributes[attribute_name]
            for poly in obj.data.polygons:
                if poly.select:
                    if self.param == "Assign":
                        attribute.data[poly.index].value = True
                    if self.param == "Remove":
                        attribute.data[poly.index].value = False

        bpy.ops.object.editmode_toggle()

        return {"FINISHED"}


class FacemapSelections(bpy.types.Operator):
    bl_idname = "mesh.facemap_selections"
    bl_label = "Facemap Selections"

    param: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        fm = context.object.data.attributes.active
        return fm is not None and fm.domain == "FACE" and fm.data_type == "BOOLEAN"

    def execute(self, context):
        obj = context.object

        facemap = context.object.data.attributes.active
        attribute_name = facemap.name

        bpy.ops.object.editmode_toggle()

        if attribute_name in obj.data.attributes:
            attribute = obj.data.attributes[attribute_name]
            for poly in obj.data.polygons:
                # if poly.select:
                if attribute.data[poly.index].value:
                    if self.param == "Select":
                        poly.select = True
                    if self.param == "Deselect":
                        poly.select = False
            edge = bpy.context.object.data.edges
            for i in edge:
                i.select = False

        bpy.ops.object.editmode_toggle()

        return {"FINISHED"}


class FMS_OT_facemap_delete(bpy.types.Operator):
    bl_idname = "fms.facemap_delete"
    bl_label = "FacemapDelete"
    bl_description = "Delete Active face map "
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        fm = context.object.data.attributes.active
        return fm is not None and fm.domain == "FACE" and fm.data_type == "BOOLEAN"

    def execute(self, context):
        bpy.ops.geometry.attribute_remove()
        return {"FINISHED"}


class MESH_UL_fmaps(UIList):

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = [
            (
                self.bitflag_filter_item
                if item.domain == "FACE" and item.data_type == "BOOLEAN"
                else 0
            )
            for item in items
        ]
        return flt_flags, []

    def draw_item(
        self,
        _context,
        layout,
        _data,
        item,
        icon,
        _active_data,
        _active_propname,
        _index,
    ):

        fmap = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.prop(fmap, "name", text="", emboss=False, icon="FACE_MAPS")

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class DATA_PT_face_maps(Panel):
    bl_label = "Face Maps"
    bl_space_type = "PROPERTIES"
    bl_context = "data"
    bl_region_type = "WINDOW"
    bl_options = {"DEFAULT_CLOSED"}
    COMPAT_ENGINES = {
        "BLENDER_RENDER",
        "BLENDER_EEVEE",
        "BLENDER_WORKBENCH",
        "BLENDER_WORKBENCH_NEXT",
    }

    # param: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def draw(self, context):
        layout = self.layout

        ob = context.object
        mesh = context.mesh
        attributes = context.object.data.attributes

        face_maps = [att for att in attributes if att.name.startswith("FaceMap")]

        facemap = mesh.attributes.active
        rows = 2
        if facemap:
            rows = 4

        row = layout.row()
        row.template_list(
            "MESH_UL_fmaps",
            "",
            ob.data,
            "attributes",
            ob.data.attributes,
            "active_index",
            rows=rows,
        )

        col = row.column(align=True)
        col.operator("mesh.facemap_create", icon="ADD", text="")
        col.operator("fms.facemap_delete", icon="REMOVE", text="")

        if len(face_maps) > 0 and (ob.mode == "EDIT" and ob.type == "MESH"):
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("mesh.facemap_assign", text="Assign").param = "Assign"
            sub.operator("mesh.facemap_assign", text="Remove").param = "Remove"

            sub = row.row(align=True)
            sub.operator("mesh.facemap_selections", text="Select").param = "Select"
            sub.operator("mesh.facemap_selections", text="Deselect").param = "Deselect"


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(FacemapSelect.bl_idname, text="From facemap")
    self.layout.operator(FacemapCreate.bl_idname, text="Create facemap")


classes = [
    FacemapSelect,
    FacemapCreate,
    FMS_OT_facemap_delete,
    FacemapAssign,
    FacemapSelections,
    MESH_UL_fmaps,
    DATA_PT_face_maps,
]


classes = [
    FacemapSelect,
    FacemapCreate,
    FMS_OT_facemap_delete,
    FacemapAssign,
    FacemapSelections,
    MESH_UL_fmaps,
    DATA_PT_face_maps,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.VIEW3D_MT_select_edit_mesh.append(menu_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    bpy.types.VIEW3D_MT_select_edit_mesh.remove(menu_func)


if __name__ == "__main__":
    register()
