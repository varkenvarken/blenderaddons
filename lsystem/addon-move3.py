import bpy
from bpy.types import Operator
from bpy.props import FloatVectorProperty, FloatProperty

class Move3Operator(bpy.types.Operator):
	"""Move3 Operator"""
	bl_idname = "object.move3_operator"
	bl_label = "Move3 Operator"
	bl_options = {'REGISTER', 'UNDO'}

	direction = FloatVectorProperty(
			name="direction",
			default=(1.0, 1.0, 1.0),
			subtype='XYZ',
			description="move direction"
			)
	
	distance = FloatProperty(
			name="distance",
			default=1.0,
			subtype='DISTANCE',
			unit='LENGTH',
			description="distance"
			)

	def execute(self, context):
		dir = self.direction.normalized()
		context.active_object.location += self.distance * dir
		return {'FINISHED'}
	
	@classmethod
	def poll(cls, context):
		ob = context.active_object
		return ob is not None and ob.mode == 'OBJECT'

def add_object_button(self, context):
	self.layout.operator(
		Move3Operator.bl_idname,
		text=Move3Operator.__doc__,
		icon='PLUGIN')

def register():
	bpy.utils.register_class(Move3Operator)
	bpy.types.VIEW3D_MT_object.append(add_object_button)

if __name__ == "__main__":
	register()