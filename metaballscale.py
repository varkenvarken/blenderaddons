# ##### BEGIN GPL LICENSE BLOCK #####
#
#  metaballscale.py
#  Scale the size of all selected meta elements 
#  (c) 2018 Michel Anders (varkenvarken)
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
	"name": "MetaballSize",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201809231640),
	"blender": (2, 79, 0),
	"location": "View3D > Metaball",
	"description": "Scale attributes of all elements in a metaball",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Metaballs"}

import bpy
from bpy.props import FloatVectorProperty, FloatProperty, EnumProperty
from bpy.types import Panel

class MetaballSize(bpy.types.Operator):
	bl_idname = "mesh.metaballsize"
	bl_label = "MetaballSize"
	bl_description = "Scale attributes of all elements in a metaball"
	bl_options = {'REGISTER', 'UNDO'}

	scale = FloatVectorProperty(name="Size", default=(1.0, 1.0, 1.0))

	radius = FloatProperty(name="Radius", default=1.0, min=0.0)

	stiffness = FloatProperty(name="Stiffness", default=1.0, min=0.0)

	type = EnumProperty(name="Type",
		items = [('KEEP','Keep','Do not change the type'),
				 ('CUBE','Cube','Cube'),
				 ('ELLIPSOID','Ellipsoid','Ellipsoid'),
				 ('PLANE','Plane','Plane'),
				 ('BALL','Ball','Ball'),
				 ('CAPSULE','Capsule','Capsule')],
		default = 'KEEP')

	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_METABALL'

	def execute(self, context):
		# we'd rather do this for just the selected elements but
		# apparently the select status is not exposed
		# see: https://blender.stackexchange.com/questions/101350/how-can-i-find-the-selected-metaball-elements-in-edit-mode-with-python
		for e in context.active_object.data.elements:
			e.size_x *= self.scale[0]
			e.size_y *= self.scale[1]
			e.size_z *= self.scale[2]
			e.radius *= self.radius
			e.stiffness *= self.stiffness
		if self.type != 'KEEP':
			for e in context.active_object.data.elements:
				e.type = self.type + ''
		return {'FINISHED'}

class DATA_PT_metaball_element_extra(Panel):
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "data"
	bl_label = "Active Element II"

	@classmethod
	def poll(cls, context):
		return (context.meta_ball and context.meta_ball.elements.active)

	def draw(self, context):
		layout = self.layout
		metaelem = context.meta_ball.elements.active
		layout.prop(metaelem, "radius", text="Radius")

def menu_func(self, context):
	self.layout.separator()
	self.layout.operator(MetaballSize.bl_idname)

def register():
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_edit_meta.append(menu_func)

def unregister():
	bpy.types.VIEW3D_MT_edit_meta.remove(menu_func)
	bpy.utils.unregister_module(__name__)
