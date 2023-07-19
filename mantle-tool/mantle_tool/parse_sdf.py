#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

"""parse_sdf.py

The module provides utility functions and classes for parsing user-provided
System Description Format XML files (SDF) to Registry objects.

It uses sel4cp_tool-derived code to actually parse the XML input (sysxml module)
and provides functions that transform the resulting SystemDescription object
ntto an actual validated Registry.
"""

from typing import (Union, Optional)

from types import MappingProxyType

from pathlib import Path
import os

from mantle_tool.sysxml import (SysMap, SysIrq, SysProtectionDomain, SysMemoryRegion,
                                SysChannel, SystemDescription, xml2system, default_platform_description)
from mantle_tool.registry import (
    ProtectionDomain, Inlet, CommChannel, IRQChannel, MappedMemoryRegion, Registry)
from mantle_tool.validation import (ValidationError, validation_errors)


class SDFParseError:
    """
    Represents an unrecoverable error encountered while the sysxml module tried to parse an
    input SDF file.

    Attributes:
    ----------
    short_error : str
        A concise, human-readable summary of the error.        

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, short_error: str) -> None:
        self.short_error = short_error

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        return self.short_error

    def format_error(self) -> str:
        """
        A detailed, human-readable error message with troubleshooting hints.

        The returned string includes additional details such as a description of the error, 
        a troubleshooting hint, and the location where the error originated.

        Returns:
        -------
        str
            The formatted error message.
        """
        title: str = "[ERROR] {title}".format(title=self.format_short_error())
        description: str = \
            "The XML/SDF file you provided could not be parsed."
        error: str = \
            "{title}\n\n{desc}\n".format(title=title, desc=description)
        return error


RegistryError = Union[SDFParseError, ValidationError]


def system_description_to_registry(the_system_desc: SystemDescription, input_filename: Optional[str] = None) -> Union[Registry, list[ValidationError]]:
    """
    Transform a SystemDescription parsed by sysxml into a Registry, performing validation checks.

    This function takes a SystemDescription object and transforms it into a Registry object.

    The transformation involves extracting protection domains, inlets, communication channels,
    IRQ channels, and mapped memory regions from the hierarchical structure of the SystemDescription,
    which closely follows the XML input.

    The function then checks if the transformed Registry is valid using the validation_errors function.
    If any errors are found, these are returned as a list of ValidationError objects.
    If no errors are found, the well-formed Registry is returned.

    Parameters
    ----------
    the_system_desc : SystemDescription
        The SystemDescription object to be transformed into a registry.
    input_file : Optional[str]
        The name of the input file if known (used only in provenance information)

    Returns
    -------
    Union[Registry, list[ValidationError]]
        The formed and validated registry if no validation errors are found,
        and a list of validation errors otherwise.

    """
    description: str = "parsed from %s" % the_system_desc
    if input_filename:
        description = "parsed from %s" % input_filename
    protection_domains: set[ProtectionDomain] = set()
    protection_domains_providing_ppcall: set[ProtectionDomain] = set()
    inlets: set[Inlet] = set()
    comm_channels: set[CommChannel] = set()
    irq_channels: set[IRQChannel] = set()
    mapped_memory_regions: set[MappedMemoryRegion] = set()
    priority_by_protection_domain: dict[ProtectionDomain, int] = dict()

    mmr_size_by_name: dict[str, int] = dict()
    for system_mr in the_system_desc.memory_regions:
        mmr_size_by_name[system_mr.name] = system_mr.size

    for system_pd in the_system_desc.protection_domains:
        pd: ProtectionDomain = \
            ProtectionDomain(system_pd.name)
        protection_domains.add(pd)
        priority_by_protection_domain[pd] = system_pd.priority
        if system_pd.pp:
            protection_domains_providing_ppcall.add(pd)
        for system_irq in system_pd.irqs:
            inlet: Inlet = Inlet(pd, system_irq.id_)
            inlets.add(inlet)
            irq_channel = IRQChannel(system_irq.irq, inlet)
            irq_channels.add(irq_channel)
        for system_map in system_pd.maps:
            if system_map.mr in mmr_size_by_name.keys():
                address: int = system_map.vaddr
                size: int = mmr_size_by_name[system_map.mr]
                writable: bool = True if 'w' in system_map.perms else False
                patch_symbol: Optional[str] = system_map.setvar_vaddr
                mmr: MappedMemoryRegion = \
                    MappedMemoryRegion(system_map.mr, pd,
                                       address, size, writable, patch_symbol)
                mapped_memory_regions.add(mmr)

    for system_channel in the_system_desc.channels:
        comm_channel_inlets: frozenset[Inlet] = \
            frozenset([Inlet(ProtectionDomain(name), number)
                      for (name, number) in system_channel.ends])
        for ci in comm_channel_inlets:
            inlets.add(ci)
        comm_channels.add(CommChannel(comm_channel_inlets))

    registry: Registry = \
        Registry(description, frozenset(protection_domains), frozenset(protection_domains_providing_ppcall), frozenset(inlets), frozenset(comm_channels), frozenset(irq_channels), frozenset(mapped_memory_regions), MappingProxyType(priority_by_protection_domain)
                 )

    validation_errors_found: list[ValidationError] = \
        validation_errors(registry)

    if validation_errors_found:
        return validation_errors_found
    return registry


def sdf_file_to_registry(input_file: Path) -> Union[Registry, list[RegistryError]]:
    """
    Parse an XML System Description File (SDF) into a Registry object, performing validation checks.

    This function attempts to parse the given XML file to a SystemDescription object using the
    parser from sysxml. Any errors that occur during parsing are recorded as SDFParseError objects
    and returned immediately.

    The function then transforms the SystemDescription object into a Registry object using the
    system_description_to_registry  function. If the transformation results in validation errors,
    these are returned as a list of registry errors.

    The function returns either a successfully generated Registry object, or if that fails,
    a list of  RegistryError objects indicating parsing and validation errors.

    Parameters
    ----------
    input_file : Path
        The path to the SDF file to be transformed into a registry.

    Returns
    -------
    Union[Registry, list[RegistryError]]
        The validated registry if no errors are found, otherwise a list of registry errors.

    """
    registry_errors: list[RegistryError] = list()

    try:
        system_description = xml2system(
            input_file, default_platform_description())
    except ValueError as e:
        registry_errors.append(SDFParseError("%s" % e))
        return registry_errors
    except FileNotFoundError as e:
        registry_errors.append(SDFParseError("%s" % e))
        return registry_errors

    registry: Union[Registry, list[ValidationError]] = \
        system_description_to_registry(
            system_description, input_filename=os.path.basename(input_file))
    if isinstance(registry, Registry):
        return registry

    for validation_error in registry:
        registry_errors.append(validation_error)

    return registry_errors
