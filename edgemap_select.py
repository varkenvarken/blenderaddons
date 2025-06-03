# ##### BEGIN GPL LICENSE BLOCK #####
#
#  edgemap_select, (c) 2025 Michel Anders (varkenvarken).
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

# This add-on allows you to select edges based on a boolean edge map, and follows closely the template of the facemap_select add-on.

bl_info = {
    "name": "EdgemapSelect",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 20250603114629),
    "blender": (4, 4, 0),
    "location": "Edit mode 3d-view, Select- -> From edgemap | Create edgemap",
    "description": "Select edges based on the active boolean edgemap or create a new edgemap",
    "warning": "",
    "wiki_url": "https://github.com/varkenvarken/blenderaddons",
    "category": "Mesh",
}

import bpy
from bpy.types import Panel, UIList


class EdgemapCreate(bpy.types.Operator):
    bl_idname = "mesh.edgemap_create"
    bl_label = "EdgemapCreate"
    bl_description = (
        "Create a new boolean edge map and set value according to current selection"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        return context.mode == "EDIT_MESH" and context.active_object.type == "MESH"

    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        edgemap = context.active_object.data.attributes.new(
            name="EdgeMap", domain="EDGE", type="BOOLEAN"
        )

        for edge in context.active_object.data.edges:
            edgemap.data[edge.index].value = edge.select
        bpy.ops.object.editmode_toggle()

        attrs = context.object.data.attributes
        attrs.active = edgemap

        return {"FINISHED"}


class EdgemapAssign(bpy.types.Operator):
    bl_idname = "mesh.edgemap_assign"
    bl_label = "EdgemapAssign"
    bl_description = "Assign or remove edges from the active edgemap"
    bl_options = {"REGISTER", "UNDO"}

    param: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        em = context.object.data.attributes.active
        return em is not None and em.domain == "EDGE" and em.data_type == "BOOLEAN"

    def execute(self, context):
        obj = context.object
        edgemap = context.object.data.attributes.active
        attribute_name = edgemap.name

        bpy.ops.object.editmode_toggle()

        if attribute_name in obj.data.attributes:
            attribute = obj.data.attributes[attribute_name]
            for edge in obj.data.edges:
                if edge.select:
                    if self.param == "Assign":
                        attribute.data[edge.index].value = True
                    if self.param == "Remove":
                        attribute.data[edge.index].value = False

        bpy.ops.object.editmode_toggle()

        return {"FINISHED"}


class EdgemapSelections(bpy.types.Operator):
    bl_idname = "mesh.edgemap_selections"
    bl_label = "Edgemap Selections"
    bl_description = "Select or deselect edges marked in the active edgemap\nShift-Select replaces the selection"
    bl_options = {"REGISTER", "UNDO"}

    param: bpy.props.StringProperty()

    @classmethod
    def poll(self, context):
        em = context.object.data.attributes.active
        return em is not None and em.domain == "EDGE" and em.data_type == "BOOLEAN"

    def execute(self, context):
        obj = context.object

        edgemap = context.object.data.attributes.active
        attribute_name = edgemap.name

        bpy.ops.object.editmode_toggle()

        if attribute_name in obj.data.attributes:
            attribute = obj.data.attributes[attribute_name]
            if not self.__shift:  # add to or remove from selection
                for edge in obj.data.edges:
                    if attribute.data[edge.index].value:
                        if self.param == "Select":
                            edge.select = True
                        if self.param == "Deselect":
                            edge.select = False
            else:  # set the selection (deselect act the same regardless whether shift is pressed)
                for edge in obj.data.edges:
                    if self.param == "Select":
                        edge.select = attribute.data[edge.index].value
                    if self.param == "Deselect" and attribute.data[edge.index].value:
                        edge.select = False

            # Deselect all faces
            for poly in bpy.context.object.data.polygons:
                poly.select = False

        bpy.ops.object.editmode_toggle()

        return {"FINISHED"}

    def invoke(self, context, event):
        self.__shift = event.shift
        return self.execute(context)


class EMS_OT_edgemap_delete(bpy.types.Operator):
    bl_idname = "ems.edgemap_delete"
    bl_label = "EdgemapDelete"
    bl_description = "Delete Active edge map "
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(self, context):
        em = context.object.data.attributes.active
        return em is not None and em.domain == "EDGE" and em.data_type == "BOOLEAN"

    def execute(self, context):
        bpy.ops.geometry.attribute_remove()
        return {"FINISHED"}


class MESH_UL_emaps(UIList):

    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = [
            (
                self.bitflag_filter_item
                if item.domain == "EDGE"
                and item.data_type == "BOOLEAN"
                and not item.is_internal
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

        emap = item
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            layout.prop(emap, "name", text="", emboss=False, icon="EDGESEL")

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon_value=icon)


class DATA_PT_edge_maps(Panel):
    bl_label = "Edge Maps"
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

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def draw(self, context):
        layout = self.layout

        ob = context.object
        mesh = context.mesh
        attributes = context.object.data.attributes

        edge_maps = [
            att
            for att in attributes
            if att.domain == "EDGE"
            and att.data_type == "BOOLEAN"
            and not att.is_internal
        ]

        edgemap = mesh.attributes.active
        rows = 2
        if edgemap:
            rows = 4

        row = layout.row()
        row.template_list(
            "MESH_UL_emaps",
            "",
            ob.data,
            "attributes",
            ob.data.attributes,
            "active_index",
            rows=rows,
        )

        col = row.column(align=True)
        col.operator("mesh.edgemap_create", icon="ADD", text="")
        col.operator("ems.edgemap_delete", icon="REMOVE", text="")

        if len(edge_maps) > 0 and (ob.mode == "EDIT" and ob.type == "MESH"):
            row = layout.row()

            sub = row.row(align=True)
            sub.operator(
                "mesh.edgemap_assign",
                text="Assign",
            ).param = "Assign"
            sub.operator("mesh.edgemap_assign", text="Remove").param = "Remove"

            sub = row.row(align=True)
            sub.operator("mesh.edgemap_selections", text="Select").param = "Select"
            sub.operator("mesh.edgemap_selections", text="Deselect").param = "Deselect"


classes = [
    EdgemapCreate,
    EMS_OT_edgemap_delete,
    EdgemapAssign,
    EdgemapSelections,
    MESH_UL_emaps,
    DATA_PT_edge_maps,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
