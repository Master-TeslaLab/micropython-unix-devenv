#!/usr/bin/env python3

# Based on build.py from micropython-lib
# https://github.com/micropython/micropython-lib/blob/master/tools/build.py

# License of micropython-lib as follows:
# 
# This file is part of the MicroPython project, http://micropython.org/
#
# The MIT License (MIT)
#
# Copyright (c) 2022 Jim Mussared
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.



# Libary build script for MicroPython
# Build all supported libaries at micropython-lib repo into mpy types.
# Libaries are copied to default sys.path location: ~/.micropython/lib

import glob
import os
import shutil
import sys
import tempfile
import logging
from pathlib import Path

logger:logging.Logger = None

# At the moment (release 1.21.1.0) in unix enviroment, micropython builtin 
#  libraries are conflicting with micropython-lib due to old implementation 
#  using unix-ffi.
# This list is used to skip the micropython builtin libraries at micropython-lib
#  compiling.
# This list is extracted from help('modules') on micropython
# example: https://github.com/micropython/micropython-lib/issues/742
BUILTIN_LIBS = {'_asyncio','_thread','argparse','array','asyncio','binascii',
                'btree','builtins','cmath','collections','cryptolib','deflate',
                'errno','ffi','framebuf','gc','hashlib','heapq','io','json',
                'machine','math','micropython','mip','os','platform','random',
                're','requests','select','socket','ssl','struct','sys','termios',
                'time','uasyncio','uctypes','websocket',}

# Convert the tagged .py file into a .mpy file and copy to output directory.
def _compile(
    tagged_path,
    target_path,
    opt,
    mpy_cross,
):
    global logger
    mpy_tempfile = tempfile.NamedTemporaryFile(mode="rb", suffix=".mpy", delete=True)
    try:
        mpy_cross.compile(
            tagged_path,
            dest=mpy_tempfile.name,
            src_path=target_path,
            opt=opt,
            mpy_cross=None,
        )
    except mpy_cross.CrossCompileError as e:
        logger.error(f'> Failed to compile {target_path}')
        logger.error(e)
        return None
    return mpy_tempfile

def build(output_path, micropython_path):
    global logger
    import manifestfile
    import mpy_cross

    path_vars = {
        "MPY_LIB_DIR": os.path.abspath(os.path.join(micropython_path, "lib/micropython-lib")),
    }

    package_list = []
    
    # For now, don't process unix-ffi. In the future this can be extended to
    # allow a way to request unix-ffi packages via mip.
    lib_dirs = ["micropython", "python-stdlib", "python-ecosys"]

    mpy_version, _mpy_sub_version = mpy_cross.mpy_version(mpy_cross=None)
    mpy_version = str(mpy_version)
    logger.info(f'Generating bytecode version {mpy_version}...')

    for lib_dir in lib_dirs:
        lib_dir = os.path.join(path_vars["MPY_LIB_DIR"], lib_dir)
        for manifest_path in glob.glob(os.path.join(lib_dir, "**", "manifest.py"), recursive=True):
            # .../foo/manifest.py -> foo
            package_name = os.path.basename(os.path.dirname(manifest_path))
            if package_name in BUILTIN_LIBS:
                logger.info(f'Skipping package {package_name}...')
                continue
            logger.info(f'Buiding package {package_name}...')

            # Compile the manifest.
            manifest = manifestfile.ManifestFile(manifestfile.MODE_COMPILE, path_vars)
            manifest.execute(manifest_path)

            # Compile all the moduels in the package.
            skip = False
            result = []
            for target in manifest.files():
                module_names = set(os.path.dirname(target.target_path).split('/'))
                if module_names & BUILTIN_LIBS:
                    logger.info(f'> Skipping module {target.target_path}...')
                    continue
                logger.info(f'> Compiling {target.target_path}...')
                if target.file_type != manifestfile.FILE_TYPE_LOCAL:
                    logger.error('> Non-local file not supported.')
                    skip = True
                    break

                if not target.target_path.endswith(".py"):
                    logger.error(f'> Target path isn\'t a .py file: {target.target_path}')
                    skip = True
                    break

                with manifestfile.tagged_py_file(target.full_path, target.metadata) as tagged_path:
                    f = _compile(tagged_path, target.target_path, target.opt, mpy_cross)
                    if f is None:
                        skip = True
                        break
                result.append({'mpy': f, 'target_path': target.target_path})

            # Only continue whole package were compiled successfully.
            if skip:
                logger.error(f'> Failed to build package {package_name}')
                for r in result:
                    if r['mpy']:
                        r['mpy'].close() # delete the temp file
                continue
            
            # Copy the .mpy files to the output directory.
            for r in result:
                target_path = os.path.join(output_path, r['target_path'])
                target_path = target_path.replace('.py', '.mpy')
                os.makedirs(os.path.dirname(target_path), mode=0o775, exist_ok=True)
                shutil.copyfile(r['mpy'].name, target_path) # 644
                r['mpy'].close() # delete the temp file

            # Build successful, add to package list.
            if len(result) > 0:
                package_list.append(package_name)

    package_list.sort()
    logger.info('Build complete.')
    logger.info(f'Build successful: {len(package_list)} packages.')
    for p in package_list:
        logger.info(f'> {p}')

def main():
    global logger
    args = {}
    args['output'] = '/root/.micropython/lib'   # default sys.path
    args['micropython'] = '/micropython'

    if args['micropython']:
        sys.path.append(os.path.join(args['micropython'], "tools"))  # for manifestfile
        sys.path.append(os.path.join(args['micropython'], "mpy-cross"))  # for mpy_cross

    logger.info(f'Output directory: {args["output"]}')
    logger.info(f'Micropython directory: {args["micropython"]}')

    build(args['output'], args['micropython'])


if __name__ == "__main__":

    path_base = Path(__file__).absolute().parent
    logger = logging.getLogger('lib_build')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(path_base / 'lib_build.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    main()
