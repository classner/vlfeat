# -*- python -*-

import os
import platform
Import("env")

# Create a temporary environment to be able to modify it locally.
lib_env = env.Clone()
# Create the build file list.
file_list = Glob('*.c')
# The library.
library = lib_env.SharedLibrary('vl', file_list)
lib_env.AppendUnique(CPPDEFINES=['VL_BUILD_DLL',
                                 '_CRT_SECURE_NO_DEPRECATE',
                                 '__LITTLE_ENDIAN__',
                                 '__SSE2__'])
lib_env.Command('python.file',
                library,
                Copy(os.path.join('python',
                                  'vlfeat'),
                     library[0]))
lib_env.Command('test.file',
                library,
                Copy(os.path.join('src'),
                     library[0]))
Return("library")
