# ##### BEGIN GPL LICENSE BLOCK #####
#
#  opengl_debug.py 
#  (c) 2019 Michel Anders (varkenvarken)
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

"""
    Module provides better readable compilation errors for OpenGL shaders.
    On successful compilation it also lists the active attributes and uniforms in the program.
    
    This was created because even with --debug-gpu-shaders Blender will show compilation errors
    on the console and will dump source code to the temp directory making it hard to correlate this 
    information and to see which error belongs to which shader.
    
    Also a very common problem is that assigning values to uniforms or attributes will fail because 
    if a attribute or uniform is not used in a shader it is aggressively optimized away.
    Thereform it is very convenient to list the *active* attributes and uniforms after linking to
    see which ones are actually used.
    
    If you have something in your code like (Note what Blender calls a shader is called a program in OpenGL):
    
    shader = gpu.types.GPUShader(vertex_shader_src, fragment_shader_src, geocode=geometry_shader_src)

    You may want to *prepend* it with the following snippet 
    (not replace it, debug_program will delete the compiled program immediately)
    
    from opengl_debug import debug_program
    debug_program(vertex_shader_src, fragment_shader_src, geometry_shader_src)
    
    All relevant information will be printed to the console.
    You can remove/disable those lines later in your production code.
"""


import os
import bgl

def gl_error(msg):
    """
    Get latest OpenGL error and print it if any along with additional message.
    """
    err = bgl.glGetError()
    if err == bgl.GL_NO_ERROR:
        return False
    print('GL Error: %d (%s)'%(err,msg))
    return True

def gl_compile_error(program_name, shader_name, shader):
    """
    Print OpenGL compilation errors, if any, for a given shader.
    
    program_name and shader_name are arbitrary human readable strings.
    shader is an int (an OpenGL shader name)
    """
    buf = bgl.Buffer(bgl.GL_INT,1)
    bgl.glGetShaderiv(shader,bgl.GL_COMPILE_STATUS,buf)
    if buf[0] == bgl.GL_TRUE:
        return False
    err = buf[0]
    charbuf = bgl.Buffer(bgl.GL_BYTE,4000)
    lenbuf = bgl.Buffer(bgl.GL_INT,1)
    bgl.glGetShaderInfoLog(shader,4000,lenbuf,charbuf)
    print('GL Error: %d (%s:%s)\n%s'%(err, program_name, shader_name, "".join(map( chr, charbuf[:lenbuf[0]]))))
    return True

def gl_link_error(msg, program):
    """
    Print OpenGL link errors, if any, for a given program.
    
    msg is an rbitrary human readable string
    program is an int (an OpenGL program name)
    """
    buf = bgl.Buffer(bgl.GL_INT,1)
    bgl.glGetProgramiv(program, bgl.GL_LINK_STATUS,buf)
    if buf[0] == bgl.GL_TRUE:
        return False
    err = buf[0]
    charbuf = bgl.Buffer(bgl.GL_BYTE,4000)
    lenbuf = bgl.Buffer(bgl.GL_INT,1)
    bgl.glGetProgramInfoLog(program,4000,lenbuf,charbuf)
    print('GL Error: %d (%s)\n%s'%(err, msg, "".join(map( chr, charbuf[:lenbuf[0]]))))
    return True

def dump_source(shadercode):
    """
    Print a string with preceding line numbers.
    
    shadercode is sourcecode with newline separated lines
    """
    for ll in enumerate(shadercode.split("\n"), start=1):
        print("[%04d] %s"%ll)

def dump_attributes_and_uniforms(program):
    """
    Print a list of all active attributes and uniforms of a linked program.
    
    program is an int (an OpenGL program name)
    """
    count = bgl.Buffer(bgl.GL_INT,1)
    size = bgl.Buffer(bgl.GL_INT,1)
    atype = bgl.Buffer(bgl.GL_INT,1)
    length = bgl.Buffer(bgl.GL_INT,1)
    name = bgl.Buffer(bgl.GL_BYTE, 128)

    print("active attributes")
    bgl.glGetProgramiv(program,bgl.GL_ACTIVE_ATTRIBUTES, count)
    for i in range(count[0]):
        bgl.glGetActiveAttrib(program, i, 128, length, size, atype, name)
        print([k for k,v in vars(bgl).items() if v == atype[0]], "".join([chr(c) for c in name.to_list()[:length[0]] if c > 0]), "[%d]"%(size[0],) if size[0]>1 else "")
    print("active uniforms")
    bgl.glGetProgramiv(program,bgl.GL_ACTIVE_UNIFORMS, count)
    for i in range(count[0]):
        bgl.glGetActiveUniform(program, i, 128, length, size, atype, name)
        print([k for k,v in vars(bgl).items() if v == atype[0]], "".join([chr(c) for c in name.to_list()[:length[0]] if c > 0]), "[%d]"%(size[0],) if size[0]>1 else "")
 
def compile_program(vshader,fshader,gshader, program_name):
    """
    Compile and link OpenGL shaders into a program.
    
    It prints any errors along with the sourcecode on the console
    After a successful linking it also shows a list of active
    attributes and uniforms.
    
    vshader, fshader and gshader are strings containing the GLSL
    source code for vertex, fragment and geometry shader respectively.
    Any of those might be None
    
    Returns an int (an OpenGL program name)
    
    program_name is arbitray human readable string
    """
    program = bgl.glCreateProgram()
    error = False
    if vshader is not None:
        vertex_shader = bgl.glCreateShader(bgl.GL_VERTEX_SHADER)
        bgl.glShaderSource(vertex_shader,vshader)
        bgl.glCompileShader(vertex_shader)
        if not gl_compile_error(program_name, "vertexshader", vertex_shader):
            bgl.glAttachShader(program, vertex_shader)
        else:
            dump_source(vshader)
            error = True
    if fshader is not None:
        fragment_shader = bgl.glCreateShader(bgl.GL_FRAGMENT_SHADER)
        bgl.glShaderSource(fragment_shader,fshader)
        bgl.glCompileShader(fragment_shader)
        if not gl_compile_error(program_name, "fragmentshader", fragment_shader):
            bgl.glAttachShader(program, fragment_shader)
        else:
            dump_source(fshader)
            error = True
    if gshader is not None:
        geometry_shader = bgl.glCreateShader(bgl.GL_GEOMETRY_SHADER)
        bgl.glShaderSource(geometry_shader,gshader)
        bgl.glCompileShader(geometry_shader)
        if not gl_compile_error(program_name, "geometryshader", geometry_shader):
            bgl.glAttachShader(program, geometry_shader)
        else:
            dump_source(gshader)
            error = True
    if not error:
        bgl.glLinkProgram(program)
        gl_link_error(program_name, program)
        dump_attributes_and_uniforms(program)
    return program 

def delete_program(program):
    """
    Delete and OpenGL program and its attached shaders.
    """
    count = bgl.Buffer(bgl.GL_INT, 1)
    shaders = bgl.Buffer(bgl.GL_INT, 10)
    bgl.glGetAttachedShaders(program, 10, count, shaders)
    for i in range(count[0]):
        bgl.glDetachShader(program, shaders[i])
        bgl.glDeleteShader(shaders[i])
    bgl.glDeleteProgram(program)
    gl_error('delete_program')

def debug_program(vshader=None,fshader=None,gshader=None, name="Debug"):
    """
    Compile and link OpenGL shaders into a program and deletes
    it again.
    
    It prints any errors along with the sourcecode on the console
    After a successful linking it also shows a list of active
    attributes and uniforms.
    
    vshader, fshader and gshader are strings containing the GLSL
    source code for vertex, fragment and geometry shader respectively.
    Any of those might be None
    Any shader code is prepended with "#version 330\n" to conform to
    the behaviour of gpu.types.GPUShader()

    name is arbitray human readable string
    """
    preamble = "#version 330\n"
    vs = preamble + vshader if vshader is not None else None
    fs = preamble + fshader if fshader is not None else None
    gs = preamble + gshader if gshader is not None else None
    delete_program(compile_program(vs, fs, gs, name))

# tiny test examples
if __name__ == "__main__":
    # output will be:
    # GL Error: 0 (Syntax error sample:vertexshader)
    # 0(7) : error C1035: assignment of incompatible types
    # 0(8) : error C0000: syntax error, unexpected '}', expecting ',' or ';' at token "}"

    # [0001] #version 330
    # [0002] 
    # [0003]     in vec3  pos;
    # [0004] 
    # [0005]     void main()
    # [0006]     {
    # [0007]         gl_Position = pos
    # [0008]     }
    # [0009] 

    vs_syntax_error = '''
    in vec3  pos;

    void main()
    {
        gl_Position = pos
    }
    '''

    debug_program(vshader=vs_syntax_error, name="Syntax error sample")
    
    # next example compiles correctly and shows that pos2 is optimzed away;
    # output will  be:
    # active attributes
    # ['GL_FLOAT_VEC3'] pos 
    # active uniforms


    vs_opt = '''
    in vec3  pos;
    in vec3  pos2;
    void main()
    {
        gl_Position = vec4(pos, 1.0);
    }
    '''

    debug_program(vshader=vs_opt, name="Optimized attribute")
