#  reportpanel.py
#
#  (c) 2017 Michel Anders
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.


import bpy
from bpy.props import FloatProperty, StringProperty
from bpy.types import Scene
from time import sleep

bl_info = {
	"name": "Report Panel",
	"author": "Michel Anders (varkenvarken)",
	"version": (0, 0, 201704080956),
	"blender": (2, 78, 0),
	"location": "Info header",
	"description": "Puts a progress indicator the info header region",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Sample scripts"}

# a regular operator. will NOT work without a hack
# it is better to use a modal operator  when doing
# time consuming things

class TestProgress(bpy.types.Operator):
	bl_idname = 'scene.testprogress'
	bl_label = 'Test Progress'
	bl_options = {'REGISTER'}

	def execute(self, context):
		context.scene.progress_indicator_text = "Heavy job"
		context.scene.progress_indicator = 0
		for tick in range(10):
			sleep(1) # placeholder for heavy work
			context.scene.progress_indicator = tick*10
			# see https://docs.blender.org/api/current/info_gotcha.html
			bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

		context.scene.progress_indicator = 101 # done
		return {"FINISHED"}

class TestProgressModal(bpy.types.Operator):
	bl_idname = 'scene.testprogressmodal'
	bl_label = 'Test Progress Modal'
	bl_options = {'REGISTER'}

	def modal(self, context, event):
		if event.type == 'TIMER':
			self.ticks += 1
		if self.ticks > 9:
			context.scene.progress_indicator = 101 # done
			context.window_manager.event_timer_remove(self.timer)
			return {'CANCELLED'}

		context.scene.progress_indicator = self.ticks*10

		return {'RUNNING_MODAL'}

	def invoke(self, context, event):
		self.ticks = 0
		context.scene.progress_indicator_text = "Heavy modal job"
		context.scene.progress_indicator = 0
		wm = context.window_manager
		self.timer = wm.event_timer_add(1.0, context.window)
		wm.modal_handler_add(self)
		return {'RUNNING_MODAL'}

def menu_func(self, context):
	self.layout.operator(TestProgress.bl_idname)
	self.layout.operator(TestProgressModal.bl_idname)

# update function to tag all info areas for redraw
def update(self, context):
	areas = context.window.screen.areas
	for area in areas:
		if area.type == 'INFO':
			area.tag_redraw()
	# this hack is only needed for NON modal operators
	# see https://docs.blender.org/api/current/info_gotcha.html
	#bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

# a variable where we can store the original draw funtion
info_header_draw = lambda s,c: None

def register():
	# a value between [0,100] will show the slider
	Scene.progress_indicator = FloatProperty(
									default=-1,
									subtype='PERCENTAGE',
									precision=1,
									min=-1,
									soft_min=0,
									soft_max=100,
									max=101,
									update=update)

	# the label in front of the slider can be configured
	Scene.progress_indicator_text = StringProperty(
									default="Progress",
									update=update)

	# save the original draw method of the Info header
	global info_header_draw
	info_header_draw = bpy.types.INFO_HT_header.draw

	# create a new draw function
	def newdraw(self, context):
		global info_header_draw
		# first call the original stuff
		info_header_draw(self, context)
		# then add the prop that acts as a progress indicator
		if (context.scene.progress_indicator >= 0 and
			context.scene.progress_indicator <= 100) :
			self.layout.separator()
			text = context.scene.progress_indicator_text
			self.layout.prop(context.scene,
								"progress_indicator",
								text=text,
								slider=True)

	# replace it
	bpy.types.INFO_HT_header.draw = newdraw

	# regular registration stuff
	bpy.utils.register_module(__name__)
	bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
	bpy.types.VIEW3D_MT_object.remove(menu_func)
	bpy.utils.unregister_module(__name__)
	global info_header_draw
	bpy.types.INFO_HT_header.draw = info_header_draw

