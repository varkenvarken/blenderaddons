# ##### BEGIN GPL LICENSE BLOCK #####
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
    "name": "Nodeset",
    "author": "Michel Anders (varkenvarken)",
    "version": (0, 0, 201707011445),
    "blender": (2, 78, 4),  # needs support for Principled shader to work
    "location": "Node Editor -> Add",
    "description": "Add a set of images and configure texture nodes based on names",
    "warning": "",
    "wiki_url": "",
    "category": "Node",
}

import bpy, blf, bgl
from bpy.types import Operator, Panel, Menu
from bpy.props import FloatProperty, EnumProperty, BoolProperty, IntProperty, StringProperty, FloatVectorProperty, CollectionProperty
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector
from os import path, listdir
from glob import glob
from copy import copy
from collections import OrderedDict as odict

# Addon prefs
class NodeSet(bpy.types.AddonPreferences):
    bl_idname = __name__

    suffix_color = StringProperty(
        name="Color Suffix",
        default='_BaseColor',
        description="Suffix that identifies the base color map")

    suffix_height = StringProperty(
        name="Height Suffix",
        default='_Height',
        description="Suffix that identifies the height map")

    suffix_metallic = StringProperty(
        name="Metallic Suffix",
        default='_Metallic',
        description="Suffix that identifies the metallic map")

    suffix_normal = StringProperty(
        name="Normal Suffix",
        default='_Normal',
        description="Suffix that identifies the normal map")

    suffix_roughness = StringProperty(
        name="Roughness Suffix",
        default='_Roughness',
        description="Suffix that identifies the roughness map")

    suffix_diffuse = StringProperty(
        name="Diffuse Suffix",
        default='_Diffuse',
        description="Suffix that identifies the diffuse map")

    suffix_glossiness = StringProperty(
        name="Glossiness Suffix",
        default='_Glossiness',
        description="Suffix that identifies the glossiness map")

    suffix_specular = StringProperty(
        name="Specular Suffix",
        default='_Specular',
        description="Suffix that identifies the specular map")


    suffix_opacity = StringProperty(
        name="Opacity Suffix",
        default='_Opacity',
        description="Suffix that identifies the opacity map")

    suffix_emission = StringProperty(
        name="Emission Suffix",
        default='_Emissive',
        description="Suffix that identifies the emission map")

    suffix_ao = StringProperty(
        name="AO Suffix",
        default='_ambient_occlusion',
        description="Suffix that identifies the ao map")

    extensions = StringProperty(
        name="Extensions",
        default='png,jpg,jpeg,exr,hdr',
        description="Comma separated list of extensions to try when looking for matching texture files")

    frame_color = FloatVectorProperty(
        name="Frame color",
        description="The color of the frame node",
        default=(0.6, 0.6, 0.6),
        min=0, max=1, step=1, precision=3,
        subtype='COLOR_GAMMA',
        size=3)

    filter_fragment = StringProperty(
        name="Filter fragment",
        default='Color',
        description="Name fragment to use when filtering list of textures")

    case_sensitive = BoolProperty(
        name="Case sensitive",
        default=False,
        description="Case sensitivity of suffix matching")

    filter_to_color = BoolProperty(
        name="Filter",
        default=True,
        description="Limit list of textures in file selector files containing Filter fragment")

    link_if_exist = BoolProperty(
        name="Link existing",
        default=True,
        description="Link to texture if textures already present in scene")

    use_objectspace = BoolProperty(
        name="Use object space",
        default=False,
        description="use object space instead of tangent space for normal map nodes")
        
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.prop(self, "suffix_color")
        col.prop(self, "suffix_diffuse")
        col.prop(self, "suffix_emission")
        col.prop(self, "suffix_glossiness")
        col.prop(self, "suffix_height")
        col.prop(self, "suffix_metallic")
        col.prop(self, "suffix_normal")
        col.prop(self, "suffix_opacity")
        col.prop(self, "suffix_roughness")
        col.prop(self, "suffix_specular")
        col.prop(self, "suffix_ao")
        col.prop(self, "case_sensitive")
        col.label(" ")
        col.prop(self, "filter_to_color")
        if self.filter_to_color:
            col.prop(self, "filter_fragment")
        col.label(" ")
        col.prop(self, "extensions")
        row = col.row()
        row.prop(self, "link_if_exist")
        row.prop(self, "use_objectspace")
        col.prop(self, "frame_color")

# from node wrangler
def node_mid_pt(node, axis):
    if axis == 'x':
        d = node.location.x + (node.dimensions.x / 2)
    elif axis == 'y':
        d = node.location.y - (node.dimensions.y / 2)
    else:
        d = 0
    return d

# mainly from node wrangler
def get_nodes_links(context):
    space = context.space_data
    tree = space.node_tree
    nodes, links = None, None
    if tree:
        nodes = tree.nodes
        links = tree.links
        active = nodes.active
        context_active = context.active_node
        # check if we are working on regular node tree or node group is currently edited.
        # if group is edited - active node of space_tree is the group
        # if context.active_node != space active node - it means that the group is being edited.
        # in such case we set "nodes" to be nodes of this group, "links" to be links of this group
        # if context.active_node == space.active_node it means that we are not currently editing group
        is_main_tree = True
        if active:
            is_main_tree = context_active == active
        if not is_main_tree:  # if group is currently edited
            tree = active.node_tree
            nodes = tree.nodes
            links = tree.links

    return nodes, links

def link_nodes(nodetree, fromnode, fromsocket, tonode, tosocket):
    socket_in = tonode.inputs[tosocket]
    socket_out = fromnode.outputs[fromsocket]
    return nodetree.links.new(socket_in, socket_out)

def sanitize(s):
    t = str.maketrans("",""," \t/\\-_:;[]")
    return s.translate(t)

# the node placement stuff at the start of execute() is from node wrangler
class NSAddMultipleImages(Operator):
    """Add a collection of textures with a common naming convention"""
    bl_idname = 'node.ns_add_multiple_images'
    bl_label = 'Open a set of images'
    bl_options = {'REGISTER', 'UNDO'}

    shader = BoolProperty(
        name="Add shader",
        default=False,
        description="Add principled shader and Normal map node")

    directory = StringProperty(subtype="DIR_PATH")

    files = CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})

    filter_glob = StringProperty(
            default="*.*",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    filepath = StringProperty(
            name="File Path",
            description="Filepath used for importing the file",
            maxlen=1024,
            subtype='FILE_PATH',
            )

    # needed for mix-ins
    order = [
        "filepath",
        ]

    @classmethod
    def poll(cls, context):
            return context.space_data.node_tree is not None

    def invoke(self, context, event):
        settings = context.user_preferences.addons[__name__].preferences
        if settings.filter_to_color:
            self.filter_glob = "*" + settings.filter_fragment + "*"
        else:
            self.filter_glob = "*.*"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    @staticmethod
    def find_in_nodes(nodes,ttype):
        for n in nodes:
            if n.label.lower().find(ttype.lower())>=0:
                return n
        return None

    def execute(self, context):
        settings = context.user_preferences.addons[__name__].preferences

        nodes, links = get_nodes_links(context)

        if nodes is None:
            return {'FINISHED'}

        addshader = (context.space_data.node_tree.type == 'SHADER' and self.shader)

        nodes_list = [node for node in nodes]
        if nodes_list:
            nodes_list.sort(key=lambda k: k.location.x)
            xloc = nodes_list[0].location.x - 220 - (320 if addshader else 0) # place new nodes at far left with enough space for new nodes
            yloc = 0
            for node in nodes:
                node.select = False
                yloc += node_mid_pt(node, 'y')
            yloc = yloc/len(nodes)
        else:
            xloc = 0
            yloc = 0

        orgx, orgy = xloc,yloc

        if context.space_data.node_tree.type == 'SHADER':
            node_type = "ShaderNodeTexImage"
        elif context.space_data.node_tree.type == 'COMPOSITING':
            node_type = "CompositorNodeImage"
        else:
            self.report({'ERROR'}, "Unsupported Node Tree type!")
            return {'CANCELLED'}

        # an ordered dictionary will cause the loaded images to be in alphabetical order
        # which is convenient because names are often quite long and hence unreadable in
        # a collapsed node
        suffixes = odict()
        if settings.suffix_color != '' :
            suffixes[settings.suffix_color] = False
        if settings.suffix_diffuse != '' :
            suffixes[settings.suffix_diffuse] = False
        if settings.suffix_emission != '' :
            suffixes[settings.suffix_emission] = False
        if settings.suffix_glossiness != '' :
            suffixes[settings.suffix_glossiness] = False
        if settings.suffix_height != '' :
            suffixes[settings.suffix_height] = False
        if settings.suffix_metallic != '' :
            suffixes[settings.suffix_metallic] = False
        if settings.suffix_normal != '' :
            suffixes[settings.suffix_normal] = False
        if settings.suffix_opacity != '' :
            suffixes[settings.suffix_opacity] = False
        if settings.suffix_roughness != '' :
            suffixes[settings.suffix_roughness] = False
        if settings.suffix_specular != '' :
            suffixes[settings.suffix_specular] = False
        if settings.suffix_ao != '' :
            suffixes[settings.suffix_ao] = False

        def endswith(s, suffix):
            if not settings.case_sensitive:
                s = s.lower()
                suffix = suffix.lower()
            return s.endswith(suffix)

        new_nodes = []
        prefix = None
        ext = None
        # first we get all explicitely selected files ...
        for f in self.files:
            fname = f.name
            basename = path.basename(path.splitext(fname)[0])
            ext = path.splitext(fname)[1]

            node = nodes.new(node_type)
            new_nodes.append(node)
            node.label = fname
            node.hide = True
            node.width_hidden = 100
            node.location.x = xloc
            node.location.y = yloc
            yloc -= 40

            img = bpy.data.images.load(self.directory+fname,settings.link_if_exist)
            node.image = img
            # we only mark a file with a color suffix as color data, all other as non color data
            node.color_space = 'COLOR' if (endswith(basename, settings.suffix_color) or endswith(basename, settings.suffix_diffuse)) else 'NONE' # that is the string NONE

            # we check if the loaded file is one in the specified list of suffixes and mark that one as seen
            for k,v in suffixes.items():
                if endswith(basename, k):
                    suffixes[k] = True
                    prefix = fname[:-len(k+ext)] # prefix is the filepath
                    node.label = sanitize(k)

        # the next step is to load additional files if a suffix is specified and the user did not explicitely select it already
        # however, if a texture was selected that has no recognized suffix, we skip this
        if prefix is not None:
            files = listdir(self.directory)
            fileslower = [f.lower() for f in files]
            #print(files)
            #print(fileslower)
            for k,v in suffixes.items():
                if not v : # haven't loaded this filename yet explicitely
                    for ext in settings.extensions.split(','):
                        fname = prefix + k + '.' + ext.strip()

                        #print('checking ',fname)
                        if settings.case_sensitive:
                            if fname not in files:
                                #print('case sensitive, NOT FOUND')
                                continue
                        else:
                            if fname.lower() not in fileslower:
                                #print('case INsensitive, NOT FOUND')
                                continue
                            for f in files:
                                if fname.lower() == f.lower():
                                    fname = f
                                    break

                        #print('loading for ',fname)
                        try:
                            img = bpy.data.images.load(self.directory+fname,settings.link_if_exist)

                            node = nodes.new(node_type)
                            new_nodes.append(node)
                            node.label = sanitize(k)
                            node.hide = True
                            node.width_hidden = 100
                            node.location.x = xloc
                            node.location.y = yloc
                            yloc -= 40

                            node.image = img
                            node.color_space = 'COLOR' if (k == settings.suffix_color or k == settings.suffix_diffuse) else 'NONE' # that is the string NONE
                            #print('found ',fname)
                            break
                        except:
                            pass


        # shift new nodes up to center of tree
        list_size = new_nodes[0].location.y - new_nodes[-1].location.y
        for node in new_nodes:
            node.select = True
            node.location.y += (list_size/2)

        # sort the y location based on the label
        sortedy = dict(zip(sorted(n.label for n in new_nodes), sorted([n.location.y for n in new_nodes], reverse=True)))
        for n in new_nodes:
            n.location.y = sortedy[n.label]

        # add the new nodes to a frame
        bpy.ops.node.add_node(type='NodeFrame')
        frm = nodes.active
        frm.label = path.basename(prefix if prefix else 'Material')
        frm.label_size = 14  # the default of 20 will extend the shrink to fit area! bug?
        frm.use_custom_color = True
        frm.color = settings.frame_color

        for node in new_nodes:
            node.parent = frm

        if addshader:
            # add a normal map node
            normalmap = nodes.new("ShaderNodeNormalMap")
            normalmap.hide = True
            normalmap.width_hidden = 80
            # using tangent space or object space is somewhat a matter of taste but because
            # tangent space normal maps together witj the experimental microdisplacement 
            # results in an all black material I prefer this option to be on by default.
            # see https://developer.blender.org/T49159
            if settings.use_objectspace:
                normalmap.space = 'OBJECT'

            bsdf = None
            # add a principled shader (this only works for Blender 2.79 or some daily builds
            try:
                bsdf = nodes.new("ShaderNodeBsdfPrincipled")
                bsdf.hide = False
                bsdf.width_hidden = 100
                bsdf.location.x = orgx + 360
                bsdf.location.y = orgy + 162
            except: # yes I know it is bad form not to be specific
                pass

            normaltex = NSAddMultipleImages.find_in_nodes(new_nodes, sanitize(settings.suffix_normal))
            if normaltex:
                link_nodes(context.space_data.node_tree,normaltex,"Color",normalmap,"Color")
                normalmap.location.x = orgx + 182
                normalmap.location.y = orgy - 42
                link_nodes(context.space_data.node_tree,normalmap,"Normal",bsdf,"Normal")
            if bsdf:
                metaltex = NSAddMultipleImages.find_in_nodes(new_nodes, sanitize(settings.suffix_metallic))
                if metaltex:
                    link_nodes(context.space_data.node_tree,metaltex,"Color",bsdf,"Metallic")
                roughnesstex = NSAddMultipleImages.find_in_nodes(new_nodes, sanitize(settings.suffix_roughness))
                if roughnesstex:
                    link_nodes(context.space_data.node_tree,roughnesstex,"Color",bsdf,"Roughness")
                colortex = NSAddMultipleImages.find_in_nodes(new_nodes, sanitize(settings.suffix_color))
                if colortex:
                    link_nodes(context.space_data.node_tree,colortex,"Color",bsdf,"Base Color")  # note the space in the name

        context.area.tag_redraw() # this in itself is not enough to trigger a redraw...

        bpy.ops.node.view_all()

        return {'FINISHED'}


def multipleimages_menu_func(self, context):
    col = self.layout.column(align=True)
    op = col.operator(NSAddMultipleImages.bl_idname, text="Set of images")
    op.shader = False
    op = col.operator(NSAddMultipleImages.bl_idname, text="Set of images + shader")
    op.shader = True
    col.separator()


def register():
    bpy.utils.register_module(__name__)

    # menu items
    bpy.types.NODE_MT_category_SH_NEW_TEXTURE.prepend(multipleimages_menu_func)
    bpy.types.NODE_PT_category_SH_NEW_TEXTURE.prepend(multipleimages_menu_func)


def unregister():
    bpy.types.NODE_MT_category_SH_NEW_TEXTURE.remove(multipleimages_menu_func)
    bpy.types.NODE_PT_category_SH_NEW_TEXTURE.remove(multipleimages_menu_func)

    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
