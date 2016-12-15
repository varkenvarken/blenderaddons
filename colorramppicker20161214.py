# ##### BEGIN GPL LICENSE BLOCK #####
#
#  colorrampicker.py , a Blender addon to pick a range of colors setpoints in a color ramp.
#  (c) 2016 Michel J. Anders (varkenvarken)
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
	"name": "ColorRampPicker",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201612141430),
	"blender": (2, 78, 0),
	"location": "Node Editor > Node > Color Ramp Picker",
	"description": "set a range of color setpoints in a selected color ramp by dragging the cursor over a sample area",
	"warning": "",
	"wiki_url": "https://cgcookiemarkets.com/vendor/varkenvarken/",
	"tracker_url": "https://cgcookiemarkets.com/vendor/varkenvarken/",
	"category": "Node"}

import bpy
import bgl

class ColorRampPicker(bpy.types.Operator):
	bl_idname = "nodes.colorramppicker"
	bl_label = "Color Ramp Picker"
	bl_description = "Color Ramp Picker"

	@classmethod
	def poll(self, context):  # only visible if we have a color ramp node selected
		return (context.space_data.type == 'NODE_EDITOR' 
			and context.active_object.active_material.use_nodes
			and context.active_object.active_material.node_tree.nodes.active.type == 'VALTORGB')

	def modal(self, context, event):
		context.area.tag_redraw()
		
		if event.type == 'MOUSEMOVE' or event.type == 'INBETWEEN_MOUSEMOVE':
			if self.record:
				# note that we record the the mouse position relative to the window (not to the region)
				self.mouse_path.append((event.mouse_x, event.mouse_y))

		elif event.type == 'LEFTMOUSE':
			if event.value == 'PRESS' and not self.record:
				self.record = True
				self.mouse_path.append((event.mouse_x, event.mouse_y))
			else: # release or second press while recording
				# bpy.types.SpaceImageEditor.draw_handler_remove(self._handle, 'WINDOW')
				if self.cursor_set: context.window.cursor_modal_restore()
				# we can only have 32 elements in a color band so we have to down sample the mouse points
				nmp = len(self.mouse_path)
				if nmp > 32:
					d = (nmp//32)+1
					self.mouse_path = self.mouse_path[::d]
				buf = bgl.Buffer(bgl.GL_FLOAT, [1, 3])
				if len(self.mouse_path) == 1:
					self.mouse_path.append(self.mouse_path[0])
				elements = context.active_object.active_material.node_tree.nodes.active.color_ramp.elements
				# remove all elements (setpoints). Last one cannot be removed
				while len(elements) > 1:
					elements.remove(elements[0])
				# set the color and the position of the first point
				# note that our recorded mouse positions are relative to the window but the framebuffer in our context
				# is also the whole window, in other words we do not have to add any offset.
				# unfortunately we can only read pixels from our own framebuffer that means we cannot sample pixels
				# outside our current window, not even another Blender window!
				wx = 0  #context.window.x
				wy = 0  #context.window.y
				x,y = self.mouse_path[0]
				bgl.glReadPixels(x+wx, y+wy, 1,1 , bgl.GL_RGB, bgl.GL_FLOAT, buf)
				e = elements[0]
				rgb = buf[0]
				e.color = (rgb[0], rgb[1], rgb[2], 1)
				e.position = 0.0
				# set the color of the other points, spacing them evenly
				delta = 1.0 / (len(self.mouse_path)-1)
				i = 0
				for x,y in self.mouse_path[1:]:
					i += 1
					bgl.glReadPixels(x+wx, y+wy, 1,1 , bgl.GL_RGB, bgl.GL_FLOAT, buf)
					rgb = buf[0]
					e = elements.new(i * delta)
					e.color = (rgb[0], rgb[1], rgb[2], 1)
				return {'FINISHED'}

		elif event.type in {'RIGHTMOUSE', 'ESC'}:
			if self.cursor_set:
				context.window.cursor_modal_restore()
			return {'CANCELLED'}

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):

		self.cursor_set = False
		if context.space_data.type == 'NODE_EDITOR':
			if context.active_object.active_material.use_nodes:
				node = context.active_object.active_material.node_tree.nodes.active
				if node and node.type == 'VALTORGB':
					args = (self, context)
					self.mouse_path = []
					context.window_manager.modal_handler_add(self)
					context.window.cursor_modal_set('EYEDROPPER')
					self.cursor_set = True
					self.record = False
					context.area.tag_redraw()
					return {'RUNNING_MODAL'}
		return {'CANCELLED'}

def menu_func_vcol(self, context):
	self.layout.operator(ColorRampPicker.bl_idname,icon='PLUGIN')

def register():
	bpy.utils.register_module(__name__)
	bpy.types.NODE_MT_node.append(menu_func_vcol)

def unregister():
	bpy.types.NODE_MT_node.remove(menu_func_vcol)
	bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
	register()
