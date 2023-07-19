#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

from hypothesis import given
import hypothesis.strategies as st

from tests.generators import (registry)

from mantle_tool.codegen import generate_api

import subprocess
import tempfile
import os

# This test is not executed by default. It's meant to run as a sanity check only
# when changes are made to the code generator.
# 
# To run it, first configure the variables libmantle_dir and austral_compiler to point
# to the libmantle directory and an Austral compiler respectively.
# 
# Once these variables are properly configured, uncomment the test below, then run the
# test suite as usual.
#
# The test will generate 50 random registries, generate APIs based on each, and execute
# the Austral compiler to verify that the resulting module files actually typecheck,
# and do not contain any syntax errors.
#
# TODO: This test does not function correctly yet - the compiler seems to emit an empty
# C file no matter what. Might be related to the --no-entrypoint option.
@given(the_registry=registry())
def code_gen_should_not_result_in_errors(the_registry):
    #libmantle_dir = "/path/to/libmantle/"
    #austral_compiler = "/path/to/austral"

    if not the_registry.protection_domains:
        return
    the_target = [t for t in the_registry.protection_domains][0]
    api = generate_api(the_registry, the_target)

    with tempfile.TemporaryDirectory() as tmpdir:
        aui_path = os.path.join(tmpdir, "generated.aui")
        with open(aui_path, 'w+') as tmp:
            for line in api.emitted_aui:
                tmp.write(line)
            tmp.flush()

        aum_path = os.path.join(tmpdir, "generated.aum")
        with open(aum_path, 'w+') as tmp:
            for line in api.emitted_aum:
                tmp.write(line)
            tmp.flush()

        libmantle_unsafe = \
          "{dir}/unsafe.aui,{dir}/unsafe.aum".format(dir=libmantle_dir)
        libmantle_common = \
          "{dir}/common.aui,{dir}/common.aum".format(dir=libmantle_dir)
        generated = \
          "%s,%s" % (aui_path, aum_path)
        out_path = os.path.join(tmpdir, "generated.c")
        completed_process = \
          subprocess.run([austral_compiler, "compile", libmantle_unsafe, libmantle_common, generated, "--no-entrypoint", "--target-type=c", "--output=%s" % out_path], stderr=subprocess.PIPE)
    assert completed_process.returncode == 0, "The Austral compiler must be able to typecheck generated code."
#code_gen_should_not_result_in_errors()
