#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

from typing import (Union, Optional)
from dataclasses import dataclass

import argparse
import sys
from pathlib import Path

from mantle_tool.registry import (ProtectionDomain, Registry)
from mantle_tool.parse_sdf import (sdf_file_to_registry, RegistryError)
from mantle_tool.codegen import (Emitter, generate_api)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.prog = "mantletool"
    parser.add_argument("-c", "--output-c", type=str,
                        help="output file for generated C headers")
    parser.add_argument("-i", "--output-aui", type=str,
                        help="output file for generated Austral interface")
    parser.add_argument("-m", "--output-aum", type=str,
                        help="output file for generated Austral module")
    parser.add_argument("-g", "--generate-api", metavar="PD_NAME",
                        type=str, help="generate an API for the given protection domain")
    parser.add_argument("input_file", type=str,
                        help="the input System Description File")
    args = parser.parse_args()

    # generate a registry from the given SDF
    registry: Registry = parse_registry_or_die(args.input_file)

    if not args.generate_api:
        # If the user didn't ask us to generate anything, we just error-check the SDF
        # file. Since we reached this point, there were no errors, and we can exit.
        sys.exit(0)

    # generate API
    target: ProtectionDomain = find_target_or_die(registry, args.generate_api)
    api: Emitter = generate_api(registry, target)

    # write outputs
    # TODO: better error reporting here

    if not (args.output_c or args.output_aui or args.output_aum):
        error_print("[WARN] An API was generated but no output was requested.")
        sys.exit(0)

    if args.output_c:
        with open(args.output_c, "w") as c_file:
            for line in api.emitted_c:
                c_file.write(line)
                c_file.write("\n")

    if args.output_aui:
        with open(args.output_aui, "w") as aui_file:
            for line in api.emitted_aui:
                aui_file.write(line)
                aui_file.write("\n")

    if args.output_aum:
        with open(args.output_aum, "w") as aum_file:
            for line in api.emitted_aum:
                aum_file.write(line)
                aum_file.write("\n")

    # all requested output was successful, we can exit
    sys.exit(0)


def error_print(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def parse_registry_or_die(input_file: Path) -> Registry:
    parsed_registry: Union[Registry, list[RegistryError]] = \
        sdf_file_to_registry(input_file)
    if not isinstance(parsed_registry, Registry):
        error_print(parsed_registry[0].format_error())
        other_errors = parsed_registry[1:]
        if len(other_errors) > 1:
            error_print("Other errors were encountered:")
        if len(other_errors) == 1:
            error_print("One other error was encountered:")
        for e in other_errors:
            error_print("  " + e.format_short_error())
        sys.exit(1)
    return parsed_registry


def find_target_or_die(registry: Registry, target: str) -> ProtectionDomain:
    possible_targets: list[ProtectionDomain] = \
        [pd for pd in registry.protection_domains if pd.name == target]
    if not possible_targets:
        error_print(
            "[ERROR] Target protection domain not found: '{name}'.".format(name=target))
        error_print("")
        error_print(
            "The given SDF does not have a protection domain with this name.")

        # suggest 3 names of similar length (potential typos)
        suggestions: list[str] = \
            [pd.name for pd in registry.protection_domains]
        suggestions.sort(key=lambda x: abs(len(x) - len(target)))

        hint: str = \
            "Hint: Did you mean one of %s?" % suggestions[:3]
        error_print(hint)
        sys.exit(1)
    return possible_targets[0]


if __name__ == "__main__":
    main()
