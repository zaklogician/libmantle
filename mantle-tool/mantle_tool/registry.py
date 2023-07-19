#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

"""registry.py

This module contains the Registry dataclass, which represents a user-specified
system description in a format optimized for further processing and code generation.

While the data layout of the SystemDescription object defined in the sysxml module
closely mirrors the user-provided SDF, the Registry object rearranges and organizes
this data, presenting some new abstractions for efficient access and manipulation
during the subsequent analysis and code generation tasks.

The module also provides utility functions and classes for checking the correctness
of Registry objects.
"""

from types import MappingProxyType
from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class ProtectionDomain:
    """
    Unique identifier of a specific protection domain within a Registry.

    Attributes
    ----------
    name : str
        the name of the Protection Domain, as specified by the user in the SDF (English letters and underscores).
    """
    name: str


@dataclass(frozen=True, eq=True)
class Inlet:
    """
    Unique identifier for a specific protection domain and channel id pair
    within a registry.

    Recall that communication channels between two protection domains, P and Q,
    can have different channel ids (channel numbers) in each. E.g. if a given
    communcation channel has channel id 5 in P and channel id 8 in Q, then
    when P sinlets a notification on channel id 5, Q will receive a notification
    coming from channel id 8, and vice versa.

    The term Inlet allows us to refer to such a pair uniquely: it signifies a
    point of entry into a specific protection domain.

    Attributes
    ----------
    protection_domain : ProtectionDomain
        the protection domain whose channel number is being referenced
    number : int
        the inlet id (channel id) within the protection domain
    """
    protection_domain: ProtectionDomain
    number: int


@dataclass(frozen=True, eq=True)
class CommChannel:
    """
    A communication channel between two protection domains, identified uniquely
    by the two inlets it connects.

    Attributes
    ----------
    inlets : frozenset[Inlet]
        a two-element set containing the inlets (ends) associated with the channel
    """
    inlets: frozenset[Inlet]


@dataclass(frozen=True, eq=True)
class IRQChannel:
    """
    A pseudo-channel connecting an Inlet to notifications from a system IRQ.

    An IRQChannel between the inlet (protection_domain, n) and the IRQ i exists in the
    Registry if the SDF declares the IRQ i mapped to channel number n in the protection
    domain declaration.

    Attributes
    ----------
    irq : int
        the number of the IRQ
    inlet : Inlet
        the inlet which is notified when an interrupt occurs
    """
    irq: int
    inlet: Inlet


@dataclass(frozen=True, eq=True)
class MappedMemoryRegion:
    """
    A contiguous region of memory that will be mapped into the the virtual address
    space of a specific protection domain at a given virtual address, with a given
    fixed set of permissions.

    Attributes
    ----------
    name : str
        the name of this memory region as specified by the user in the SDF
    protection_domain : ProtectionDomain
        the protection domain whose VSpace this memory region is mapped into
    address : int
        the virtual address at which the given memory region starts
    size : int
        the size of the memory region in smallest addressable units
    writable : bool
        True precisely if the memory region is mapped with write permissions
    patch_symbol : Optional[str]
        the variable/symbol name in the final executable into which the address
        will be patched by the sel4cp_tool using the setvar mechanism (if any)
    """
    name: str
    protection_domain: ProtectionDomain
    address: int
    size: int
    writable: bool
    patch_symbol: Optional[str]


@dataclass(frozen=True, eq=True)
class Registry:
    """
    A description of all the seL4 Core Platform objects and properties relevant
    to code generation in Mantle, derived from a user-specified system description.

    The registry contains information about protection domains, communication channels, 
    IRQ channels, mapped memory regions, and priority levels of protection domains.
    It also keeps track of which protection domains provide protected procedure calls.

    Attributes:
    ----------
    description: str
        A one-line human-readable string describing the registry and its provenance (how it was
        created and from which resource).

    protection_domains: frozenset[ProtectionDomain]
        The set of all valid protection domains in the system represented by this Registry.

    protection_domains_providing_pp: frozenset[ProtectionDomain]
        The set of all protection domains that allow lower-priority protection domains
        to make protected procedure calls.

    inlets: frozenset[Inlet]
        The set of all valid inlets in the system.

    comm_channels: frozenset[CommChannel]
        The set of all valid communication channels in the system.

    irq_channels: frozenset[IRQChannel]
        The set of all valid interrupt request (IRQ) channels in the system.

    mappedmemoryregions: frozenset[MappedMemoryRegion]
        The set of all mapped memory regions in the system.

    priority_by_protection_domain: MappingProxyType[ProtectionDomain, int]
        An immutable dictionary that associates each protection domain to its priority level.
    """
    description: str
    protection_domains: frozenset[ProtectionDomain]
    protection_domains_providing_ppcall: frozenset[ProtectionDomain]
    inlets: frozenset[Inlet]
    comm_channels: frozenset[CommChannel]
    irq_channels: frozenset[IRQChannel]
    mapped_memory_regions: frozenset[MappedMemoryRegion]
    priority_by_protection_domain: MappingProxyType[ProtectionDomain, int]

    def debug_string(self) -> str:
        line1: str = "PDs:     %s\n" % sorted(
            [pd.name for pd in self.protection_domains])
        line2: str = "PDs ppc: %s\n" % sorted(
            [pd.name for pd in self.protection_domains_providing_ppcall])
        line3: str = "Inlets:  %s\n" % sorted(
            [(i.protection_domain.name, i.number) for i in self.inlets])
        line4: str = "commch:  %s\n" % sorted([(list(c.inlets)[0].protection_domain.name, list(c.inlets)[0].number, list(
            c.inlets)[1].number, list(c.inlets)[1].protection_domain.name) for c in self.comm_channels])
        line5: str = "irqch:   %s\n" % sorted(
            [(i.inlet.protection_domain.name, i.inlet.number, i.irq) for i in self.irq_channels])
        line6: str = "mmrs:    %s\n" % sorted(
            [(mmr.protection_domain.name, mmr.name) for mmr in self.mapped_memory_regions])
        return (line1 + line2 + line3 + line4 + line5 + line6)
