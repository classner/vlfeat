# -*- python -*-
# Copyright 2014 Christoph Lassner.

import os
import sys
import platform
import subprocess
from SConsChecks import AddLibOptions, GetLibChecks

_libs = ['boost.python',
         'numpy']

_checks = GetLibChecks(_libs)

def getRequiredLibs():
  if GetOption('with_python'):
    req_libs = _libs
  else:
    req_libs = []
  return req_libs

# Setup command-line options
def setupOptions():
    AddOption("--with-python", dest="with_python",
              action="store_true", help="enables building the python library",
              default=False)
    AddOption("--with-tests", dest="with_tests",
              action="store_true", help="enables building the tests",
              default=False)
    AddOption("--rpath", dest="custom_rpath", type="string", action="append",
              help="runtime link paths to add to libraries and executables (unix); may be passed more than once")
    # Add library configuration options.
    AddLibOptions(AddOption, _libs)
    # Default variables.
    variables = Variables()
    if platform.system() == 'Windows':
      default_flags = '/Ox'
    else:
      default_flags = '-O3 -g'
    variables.Add("CCFLAGS", default=os.environ.get("CCFLAGS", default_flags), help="compiler flags")
    return variables

def makeEnvironment(variables):
    shellEnv = {}
    # Some of these don't make sense on Windows, but don't hurt.
    for key in ("PATH", "LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "PYTHONPATH"):
        if key in os.environ:
            shellEnv[key] = os.environ[key]
    env = Environment(variables=variables, ENV=shellEnv)
    if env.Dictionary().has_key("CCFLAGS"):
        if isinstance(env['CCFLAGS'], basestring):
            env['CCFLAGS'] = env['CCFLAGS'].split()
    if os.environ.has_key("CCFLAGS"):
        env.AppendUnique(CCFLAGS=os.environ.get("CCFLAGS").split())
    if env['CC'] == 'cl':
        # If remove g flag.
        env.Replace(CCFLAGS=[flag for flag in env['CCFLAGS'] if flag not in ['-g']])
        # Enable C++ exception handling.
        env.Append(CCFLAGS=['/EHsc'])
    custom_rpath = GetOption("custom_rpath")
    if custom_rpath is not None:
        env.AppendUnique(RPATH=custom_rpath)
    boost_lib = GetOption('boost_lib')
    if boost_lib is not None:
        env.PrependUnique(LIBPATH=boost_lib)
    if env['CC'] == 'cl':
        env.AppendUnique(LINKFLAGS='/SUBSYSTEM:CONSOLE')
    # Enable creation of debug symbols.
    env.AppendUnique(LINKFLAGS=['-debug'])
    env.AppendUnique(CPPDEFINES='NDEBUG')
    if env['CC'] == 'cl':
      env.AppendUnique(CPPFLAGS=['/MD'])
      env.Append(LINKFLAGS = ["/DEBUG", "/LTCG"])
      env.Append(CCFLAGS = ["/Zi", "/Fd${TARGET}.pdb", '/GL', '/fp:fast'])
      env.AppendUnique(CPPFLAGS=['/nologo'])
    elif env['CC'] == 'g++':
      env.AppendUnique(CPPFLAGS='-msse2 -fPIC -pipe')
      env.AppendUnique(LINKFLAGS='-msse -shared')
      env.AppendUnique(CPPFLAGS=' -funroll-all-loops -ffast-math -ftree-vectorize')
    elif env['CC'] == 'icc':
      env.AppendUnique(CPPFLAGS='-fPIC -pipe')
      env.AppendUnique(LINKFLAGS='-shared')
      env.AppendUnique(CPPFLAGS=' -axTPW -unroll -rcd')
    return env

def setupTargets(env, root="."):
    library = SConscript(os.path.join(root, "vl", "SConscript.py"),
                         exports='env',
                         variant_dir='build/vlfeat')
    if GetOption('with_python'):
      python_module = SConscript(os.path.join(root, "python", "vlfeat", "SConscript.py"),
                                 exports=['env', 'library'],
                                 variant_dir='build/pyvlfeat')
    if GetOption('with_tests'):
      SConscript(os.path.join(root, "src", "SConscript.py"),
                               exports=['env', 'library'],
                               variant_dir='build/vltest')

Return("setupOptions",
       "makeEnvironment",
       "setupTargets",
       "_checks",
       "getRequiredLibs")
