#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

from types import MappingProxyType
from dataclasses import dataclass

import hypothesis.strategies as st
from hypothesis.control import (assume)
from mantle_tool.registry import (ProtectionDomain, MappedMemoryRegion, Inlet, CommChannel, IRQChannel, Registry)

@st.composite
def legal_name(draw):
    legal_head = "abcdefghijklmnopqrstuvwxyzABC"
    legal_tail = legal_head + "_0123456789"
    head = draw(st.text(legal_head,min_size=1,max_size=1))
    size = draw(st.sampled_from([0,3,5]))
    tail = draw(st.text(legal_tail,min_size=size,max_size=15))
    return (head + tail)

@st.composite
def legal_inlet_number(draw):
    number = draw(st.sampled_from(range(0,63)))
    return number

@st.composite
def protection_domain(draw):
    name = draw(legal_name())
    return ProtectionDomain(str(name))

@st.composite
def comm_channel(draw, existing_protection_domains, existing_comm_channels, existing_irq_channels):
    used_inlets_comm = [inlet for channel in existing_comm_channels for inlet in channel.inlets]
    used_inlets_irq = [channel.inlet for channel in existing_irq_channels]
    used_inlets = used_inlets_comm + used_inlets_irq
    while True:
        pd1 = draw(st.sampled_from(existing_protection_domains))
        id1 = draw(legal_inlet_number())
        if not (Inlet(pd1,id1) in used_inlets):
            break
        continue
    while True:
        pd2 = draw(st.sampled_from(existing_protection_domains))
        id2 = draw(legal_inlet_number())
        if not (Inlet(pd2,id2) in used_inlets):
            break
        continue
    assume(pd1 != pd2)
    assume(id1 != id2)
    return CommChannel(frozenset([Inlet(pd1,id1), Inlet(pd2,id2)]))

@st.composite
def irq_channel(draw, existing_protection_domains, existing_comm_channels, existing_irq_channels):
    used_inlets_comm = [inlet for channel in existing_comm_channels for inlet in channel.inlets]
    used_inlets_irq = [channel.inlet for channel in existing_irq_channels]
    used_inlets = used_inlets_comm + used_inlets_irq
    used_irqs = [channel.irq for channel in existing_irq_channels]+[0]
    while True:
        pd = draw(st.sampled_from(existing_protection_domains))
        id = draw(legal_inlet_number())
        if not (Inlet(pd,id) in used_inlets):
            break
        continue
    return IRQChannel(max(used_irqs)+1, Inlet(pd,id))

@st.composite
def mapped_memory_region(draw, existing_protection_domains, exisiting_memory_regions):
    create_new = draw(st.sampled_from([False,False,True]))
    if exisiting_memory_regions and (not create_new):
        base_region = draw(st.sampled_from(exisiting_memory_regions))
        name = base_region.name
        size = base_region.size
    else:
        create_new = True
        name = draw(legal_name())
        size = draw(st.sampled_from([4096, 2097152]))        
    protection_domain = draw(st.sampled_from(existing_protection_domains))
    address = draw(st.sampled_from([0x3938d500, 0xe8365a00, 0xa5fb0a00, 0x9db56b00, 0xfffdd400]))
    writable = draw(st.sampled_from([False,True]))
    patch_symbol_name = draw(legal_name())
    patch_symbol = draw(st.sampled_from([None,patch_symbol_name]))
    if not create_new and base_region.protection_domain == protection_domain:
        patch_symbol = patch_symbol_name
    return MappedMemoryRegion(name, protection_domain, address, size, writable, patch_symbol)

@dataclass(frozen=False, eq=True)
class Preregistry:
    # a non-frozen version of a registry that we can manipulate to create test cases
    protection_domains: list[ProtectionDomain]
    protection_domains_providing_ppcall: list[ProtectionDomain]
    inlets: list[Inlet]
    comm_channels: list[CommChannel]
    irq_channels: list[IRQChannel]
    mapped_memory_regions: list[MappedMemoryRegion]
    priority_by_protection_domain: dict[ProtectionDomain, int]

    def to_registry(self) -> Registry:
        result = Registry( "randomly generated test registry (preregistry)" \
                         , frozenset(self.protection_domains) \
                         , frozenset(self.protection_domains_providing_ppcall) \
                         , frozenset(self.inlets) \
                         , frozenset(self.comm_channels) \
                         , frozenset(self.irq_channels) \
                         , frozenset(self.mapped_memory_regions) \
                         , MappingProxyType(self.priority_by_protection_domain) \
                         )
        return result


@st.composite
def preregistry(draw):
    existing_protection_domains = list(draw(st.lists(protection_domain(), min_size=1, max_size=6)))
    exisiting_memory_regions = list()
    existing_comm_channels = list()
    existing_irq_channels = list()

    while len(exisiting_memory_regions) < len(existing_protection_domains) - 2:
        new_memory_region = draw(mapped_memory_region(existing_protection_domains, exisiting_memory_regions))
        exisiting_memory_regions.append(new_memory_region)

    comm_count = draw(st.sampled_from([2,3]))
    while len(existing_comm_channels) < comm_count:
        new_comm_channel = draw(comm_channel(existing_protection_domains, existing_comm_channels, existing_irq_channels))
        existing_comm_channels.append(new_comm_channel)
    
    irq_count = draw(st.sampled_from([1,2]))
    while len(existing_irq_channels) < irq_count:
        new_irq_channel = draw(irq_channel(existing_protection_domains, existing_comm_channels, existing_irq_channels))
        existing_irq_channels.append(new_irq_channel)

    priority_by_protection_domain = dict()
    priority_count = 254
    for pd in existing_protection_domains:
        priority_by_protection_domain[pd] = priority_count
        priority_count = priority_count - 1

    protection_domains_providing_ppcall = existing_protection_domains[2:]

    used_inlets_comm = [inlet for channel in existing_comm_channels for inlet in channel.inlets]
    used_inlets_irq = [channel.inlet for channel in existing_irq_channels]
    used_inlets = used_inlets_comm + used_inlets_irq

    result = Preregistry( existing_protection_domains \
                        , protection_domains_providing_ppcall \
                        , used_inlets \
                        , existing_comm_channels \
                        , existing_irq_channels \
                        , exisiting_memory_regions \
                        , priority_by_protection_domain \
                        )
    return result

@st.composite
def registry(draw):
    description = "randomly generated test registry"
    existing_protection_domains = list(draw(st.lists(protection_domain(), min_size=1, max_size=6)))
    exisiting_memory_regions = list()
    existing_comm_channels = list()
    existing_irq_channels = list()

    while len(exisiting_memory_regions) < len(existing_protection_domains) - 2:
        new_memory_region = draw(mapped_memory_region(existing_protection_domains, exisiting_memory_regions))
        exisiting_memory_regions.append(new_memory_region)

    comm_count = draw(st.sampled_from([0,2,3]))
    while len(existing_comm_channels) < comm_count:
        new_comm_channel = draw(comm_channel(existing_protection_domains, existing_comm_channels, existing_irq_channels))
        existing_comm_channels.append(new_comm_channel)
    
    irq_count = draw(st.sampled_from([0,1,2]))
    while len(existing_irq_channels) < irq_count:
        new_irq_channel = draw(irq_channel(existing_protection_domains, existing_comm_channels, existing_irq_channels))
        existing_irq_channels.append(new_irq_channel)

    priority_by_protection_domain = dict()
    priority_count = 254
    for pd in existing_protection_domains:
        priority_by_protection_domain[pd] = priority_count
        priority_count = priority_count - 1

    protection_domains_providing_ppcall = existing_protection_domains[2:]

    used_inlets_comm = [inlet for channel in existing_comm_channels for inlet in channel.inlets]
    used_inlets_irq = [channel.inlet for channel in existing_irq_channels]
    used_inlets = used_inlets_comm + used_inlets_irq

    result = Registry( description \
                     , frozenset(existing_protection_domains) \
                     , frozenset(protection_domains_providing_ppcall) \
                     , frozenset(used_inlets) \
                     , frozenset(existing_comm_channels) \
                     , frozenset(existing_irq_channels) \
                     , frozenset(exisiting_memory_regions) \
                     , MappingProxyType(priority_by_protection_domain) \
                     )
    return result
