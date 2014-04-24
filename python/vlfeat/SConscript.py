# -*- python -*-

import os
import platform
Import("env", "library")

# Create a temporary environment to be able to modify it locally.
lib_env = env.Clone()
# Create the build file list.
file_list = Glob('mser/*.cpp') + \
            Glob('sift/*.cpp') + \
            Glob('imop/*.cpp') + \
            Glob('misc/*.cpp') + \
            Glob('kmeans/*.cpp') + \
            Glob('quickshift/*.cpp') + \
            ['py_vlfeat.cpp']
# Add the header dir.
lib_env.AppendUnique(CPPPATH=['../../../'])
# Add the library.
lib_env.AppendUnique(LIBS=[library[1]])

# The library.
lib_file = lib_env.SharedLibrary('_vlfeat', file_list)
# Copy it to the target directory.
if platform.system() == 'Windows':
  target_suffix = 'pyd'
else:
  target_suffix = 'so'
lib_env.Command('target.file',
                lib_file,
                Copy(os.path.join('python',
                                  'vlfeat',
                                  '_vlfeat.') + target_suffix,
                    lib_file[0]))
Return("lib_file")
