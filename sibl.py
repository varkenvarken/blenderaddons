# sibl.py (c) 2013 Michel J. Anders (varkenvarken)
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****

bl_info = {
    "name": "Add Environment Nodes",
    "author": "Michel J. Anders (varkenvarken)",
    "version": (1, 0, 20150313),
    "blender": (2, 73, 0),
    "location": "Node  editor > Add > Add Sibl Environment, Add General Environment",
    "description": "Adds environment lighting based on .ibl file or separate background and .hdr files",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Node"}

import configparser
import os.path

import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper

def add_node(context, nodetype, settings = {}):
    bpy.ops.node.add_node(type=nodetype.__name__)
    node = context.active_node
    for key,val in settings.items():
        setattr(node,key,val)
    return node

def get_node(context,nodetype, settings = {}):
    space = context.space_data
    nodetree = space.node_tree
    for n in nodetree.nodes:
        if isinstance(n, nodetype):
            return n
    return add_node(context, nodetype, settings)

def link_nodes(nodetree, fromnode, fromsocket, tonode, tosocket):
    socket_in = tonode.inputs[tosocket]
    socket_out = fromnode.outputs[fromsocket]
    return nodetree.links.new(socket_in, socket_out)
    
def main(operator,context,bg=None,ev=None):
    space = context.space_data
    node_tree = space.node_tree
    node_active = context.active_node
    node_selected = context.selected_nodes
    
    if operator.replace_all_nodes :
        node_tree.nodes.clear()
    
    W = 200
    H = 100
    bg1 = add_node(context, bpy.types.ShaderNodeBackground,
        {'location': [2*W,0], 'hide':True})
    bg2 = add_node(context, bpy.types.ShaderNodeBackground,
        {'location': [2*W,2*H], 'hide':True})
    wo = get_node(context, bpy.types.ShaderNodeOutputWorld,
        {'location': [3*W,int(1.5*H)], 'hide':True})
    mx = add_node(context, bpy.types.ShaderNodeMixShader,
        {'location': [int(2.5*W),int(1.5*H)], 'hide':True})
    ev1 = add_node(context, bpy.types.ShaderNodeTexEnvironment,
        {'location': [W,H]})
    if bg is not None:
        ev1.image = bg
    else:
        ev1.use_custom_color = True
        ev1.color = [1,0,0]
    ev2 = add_node(context, bpy.types.ShaderNodeTexEnvironment,
        {'location': [W,4*H]})
    if ev is not None:
        ev2.image = ev
    else:
        ev2.use_custom_color = True
        ev2.color = [1,0,0]
    lp = get_node(context, bpy.types.ShaderNodeLightPath,
        {'location': [W,int(1.5*H)], 'hide':True})
    mp = add_node(context, bpy.types.ShaderNodeMapping,
        {'location': [-W,2*H]})
    tx = get_node(context, bpy.types.ShaderNodeTexCoord,
        {'location': [-2*W,2*H], 'hide':True})

    link_nodes(node_tree, mx, "Shader", wo, "Surface")
    link_nodes(node_tree, bg1, "Background", mx, 2)
    link_nodes(node_tree, bg2, "Background", mx, 1)
    link_nodes(node_tree, lp, "Is Camera Ray", mx, "Fac")
    link_nodes(node_tree, ev1, "Color", bg1, "Color")
    link_nodes(node_tree, ev2, "Color", bg2, "Color")
    link_nodes(node_tree, mp, "Vector", ev1, "Vector")
    link_nodes(node_tree, mp, "Vector", ev2, "Vector")
    link_nodes(node_tree, tx, "Generated", mp, "Vector")

def first(*args):
    for i in args:
        if i != "":
            return i
    return None
    
class SiblEnvironment(bpy.types.Operator, ImportHelper):
#    """Create world environment nodes from SIBL archive"""
    bl_idname = "node.sibl_environment"
    bl_label = "Sibl Environment"

    filename_ext = ".ibl"

    filter_glob = StringProperty(
            default="*.ibl",
            options={'HIDDEN'},
            )

    directory = StringProperty(
            name="Directory",
            description="Directory used for importing the file",
            maxlen=1024,
            subtype='DIR_PATH',
            )

    replace_all_nodes = BoolProperty(name="Replace All Nodes",
        description="Delete all existing world nodes before adding sibl nodes",
        default=True)

    use_reflection_map = BoolProperty(name="Use Reflection Map",
        description="Use Reflection map if present (Environment map otherwise)",
        default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'use_reflection_map')
        layout.prop(self, 'replace_all_nodes')

    @classmethod
    def poll(cls, context):
        space = context.space_data
        # TODO add additional restriction cycles only
        return space.type == 'NODE_EDITOR' and space.shader_type == 'WORLD' and space.tree_type == 'ShaderNodeTree' and context.scene.world.use_nodes

    def execute(self, context):
        if self.filepath != "":
            config = configparser.ConfigParser()
            config.read(self.filepath)
            
            # note that the enviroment section is misspelled in the .ibl!
            # if that's ever corrected this will still work
            try:
                evf0 = config['Environment']['EVfile'].strip('"')
            except KeyError:
                evf0 = config['Enviroment']['EVfile'].strip('"')
            bgf0 = config['Background']['BGfile'].strip('"')
            ref0 = config['Reflection']['REFfile'].strip('"')
            
            bgf = first(bgf0, ref0, evf0)
            evf = first(evf0, ref0, bgf0)
            ref = first(ref0, bgf0, evf0)
            if self.use_reflection_map:
                evf = ref
            bg = None
            ev = None
            try:
                bg = bpy.data.images.load(os.path.join(self.directory, bgf))
            except RuntimeError:
                pass
            try:
                ev = bpy.data.images.load(os.path.join(self.directory, evf))
            except RuntimeError:
                pass
            main(self,context,bg,ev)
        else:
            return {'CANCELLED'}
        return {'FINISHED'}

class GeneralEnvironment(bpy.types.Operator, ImportHelper):
#    """Create world environment nodes from separate files 3"""
    bl_idname = "node.general_environment"
    bl_label = "General Environment"

    files = CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})

    directory = StringProperty(
            name="Directory",
            description="Directory used for importing the file",
            maxlen=1024,
            subtype='DIR_PATH',
            )

    filter_image = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    filter_folder = BoolProperty(default=True, options={'HIDDEN', 'SKIP_SAVE'})
    
    replace_all_nodes = BoolProperty(name="Replace All Nodes",
        description="Delete all existing world nodes before adding environment nodes",
        default=True)

    use_reflection_map = BoolProperty(name="Use Reflection Map",
        description="Use Reflection map if present (Environment map otherwise)",
        default=False)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'use_reflection_map')
        layout.prop(self, 'replace_all_nodes')


    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'replace_all_nodes')

    @classmethod
    def poll(cls, context):
        space = context.space_data
        # TODO add additional restriction cycles only
        return space.type == 'NODE_EDITOR' and space.shader_type == 'WORLD' and space.tree_type == 'ShaderNodeTree' and context.scene.world.use_nodes

    def execute(self, context):
        print(self.directory)
        for f in self.files:
            print(f.name)
        if len(self.files) > 0 and len(self.files) < 3:
            bgf=self.files[0].name
            evf=bgf
            if len(self.files) > 1:
                evf = self.files[1].name
                (name, ext) = os.path.splitext(evf)
                if ext not in {'.hdr','.exr'}:
                    t = bgf; bgf = evf; evf = t
            bg = None
            ev = None
            try:
                bg = bpy.data.images.load(os.path.join(self.directory, bgf))
            except RuntimeError:
                pass
            try:
                ev = bpy.data.images.load(os.path.join(self.directory, evf))
            except RuntimeError:
                pass
            main(self,context,bg,ev)
        else:
            return {'CANCELLED'}
        return {'FINISHED'}

def menu_func_sibl(self, context):
    self.layout.operator(SiblEnvironment.bl_idname, 
        text="Add Sibl Environment",
        icon='PLUGIN')

def menu_func_gen(self, context):
    self.layout.operator(GeneralEnvironment.bl_idname, 
        text="Add General Environment",
        icon='PLUGIN')

def register():
    bpy.utils.register_class(SiblEnvironment)
    bpy.types.NODE_MT_add.append(menu_func_sibl)
    bpy.utils.register_class(GeneralEnvironment)
    bpy.types.NODE_MT_add.append(menu_func_gen)

def unregister():
    bpy.utils.unregister_class(SiblEnvironment)
    bpy.utils.unregister_class(GeneralEnvironment)

if __name__ == "__main__":
    register()
