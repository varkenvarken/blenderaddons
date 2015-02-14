"""
A simple l-system 
"""
from math			import radians
from random			import random, seed
from collections	import namedtuple

from mathutils		import Vector,Matrix

Quad   = namedtuple('Quad', 'pos, up, right, forward')
Edge   = namedtuple('Edge', 'start, end, radius')
BObject = namedtuple('BObject', 'name, pos, up, right, forward')

class Turtle:

	def __init__(	self,
					tropism=(0,0,0),
					tropismsize=0,
					angle=radians(30),
					iseed=42 ):
		self.tropism = Vector(tropism).normalized()
		self.magnitude = tropismsize
		self.forward = Vector((1,0,0))
		self.up = Vector((0,0,1))
		self.right = self.forward.cross(self.up)
		self.stack = []
		self.position = Vector((0,0,0))
		self.angle = angle
		self.radius = 0.1
		self.__init_terminals()
		seed(iseed)
		
	def __init_terminals(self):
		"""
		Initialize a map of predefined terminals.
		"""
		self.terminals = {
			'+': self.term_plus,
			'-': self.term_minus,
			'[': self.term_push,
			']': self.term_pop,
			'/': self.term_slash,
			'\\': self.term_backslash,
			'<': self.term_less,
			'>': self.term_greater,
			'&': self.term_amp,
			'!': self.term_expand,
			'@': self.term_shrink,
			'#': self.term_fatten,
			'%': self.term_slink,
			'F': self.term_edge,
			'Q': self.term_quad,
			# '{': self.term_object
			}   
	
	def apply_tropism(self):
		# tropism is a normalized vector
		t = self.tropism * self.magnitude
		tf=self.forward + t
		tf.normalize()
		q = tf.rotation_difference(self.forward)
		self.forward.rotate(q)
		self.up.rotate(q)
		self.right.rotate(q)
		
	def term_plus(self, value=None):
		val = radians(value) if not value is None else self.angle
		r = Matrix.Rotation(val, 4, self.right)
		self.forward.rotate(r)
		self.up.rotate(r)
		
	def term_minus(self, value=None):
		val = radians(value) if not value is None else self.angle
		r = Matrix.Rotation(-val, 4, self.right)
		self.forward.rotate(r)
		self.up.rotate(r)
		
	def term_amp(self, value=30):
		k = (random()-0.5) * value
		self.term_plus(value=k)
		k = (random()-0.5) * value
		self.term_slash(value=k)
		
	def term_slash(self, value=None):
		r = Matrix.Rotation(radians(value) if not value is None
							else self.angle, 4, self.up)
		self.forward.rotate(r)
		self.right.rotate(r)
		
	def term_backslash(self, value=None):
		r = Matrix.Rotation(-radians(value) if not value is None
							else -self.angle, 4, self.up)
		self.forward.rotate(r)
		self.right.rotate(r)
		
	def term_less(self, value=None):
		r = Matrix.Rotation(radians(value) if not value is None
							else self.angle, 4, self.forward)
		self.up.rotate(r)
		self.right.rotate(r)
		
	def term_greater(self, value=None):
		r = Matrix.Rotation(-radians(value) if not value is None
							else -self.angle, 4, self.forward)
		self.up.rotate(r)
		self.right.rotate(r)
		
	def term_pop(self, value=None):
		t = self.stack.pop()
		(	self.forward,
			self.up,
			self.right,
			self.position,
			self.radius ) = t
		
	def term_push(self, value=None):
		t = (	self.forward.copy(),
				self.up.copy(),
				self.right.copy(),
				self.position.copy(),
				self.radius )
		self.stack.append(t)
	
	def term_expand(self, value=1.1):
		self.forward *= value
		self.up *= value
		self.right *= value
		
	def term_shrink(self, value=0.9):
		self.forward *= value
		self.up *= value
		self.right *= value
		
	def term_fatten(self, value=1.1):
		self.radius *= value
		
	def term_slink(self, value=0.9):
		self.radius *= value
		
	def term_edge(self, value=None):
		s = self.position.copy()
		self.apply_tropism()
		self.position += self.forward
		e = self.position.copy()
		return Edge(start=s, end=e, radius=self.radius)
	
	def term_quad(self, value=0.5):
		return Quad(pos=self.position,
					right=self.right,
					up=self.up,
					forward=self.forward )
		
	def term_object(self, value=None, name=None):
		s = self.position.copy()
		self.apply_tropism()
		self.position += self.forward
		return BObject(name=name,
					pos=s,
					right=self.right,
					up=self.up,
					forward=self.forward )
		
	def interpret(self, s):
		"""
		interpret the iterable s, yield Quad, Edge or Object named tuples.
		"""
		print('interpret:',s)
		name=''
		for c in s:
			t = None
			print(c,name)
			if c == '}':
				t = self.term_object(name=name[1:])
				name=''
			elif c == '{' or name != '':
				name += c
				continue
			elif name != '':
				continue
			elif c in self.terminals:
				t = self.terminals[c]()
			print('yield',t)
			if not t is None:
				yield t
