#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

from hypothesis import given
from hypothesis.control import assume
import hypothesis.strategies as st

from tests.generators import (preregistry, registry)
from mantle_tool.registry import (ProtectionDomain, Inlet, CommChannel, IRQChannel, MappedMemoryRegion, Registry)
from mantle_tool.validation import (ValidationError, validation_errors, InvalidInletProtectionDomain, InvalidCommChannelDuplicate, InvalidIRQChannelDuplicate)

@given(the_registry=registry())
def randomly_generated_registry_passes_validation(the_registry):
    verr = validation_errors(the_registry)
    assert (not verr), "A randomly generated registry must not produce validation errors."
randomly_generated_registry_passes_validation()


@given(the_registry=preregistry())
def invalid_inlet_protection_domain(the_registry):
    assume(the_registry.inlets)

    # we pick a PD that's actually used by a channel or IRQ mapping
    excluded_name = the_registry.inlets[0].protection_domain.name
    # then remove it from the registry
    the_registry.protection_domains = \
      [pd for pd in the_registry.protection_domains if pd.name != excluded_name]
    final_registry = the_registry.to_registry()
    # this should trigger an InvalidInletProtectionDomain validation error
    
    verrs = validation_errors(final_registry)
    for verr in verrs:
        verr.format_error()
        if isinstance(verr, InvalidInletProtectionDomain):
            return
    assert False, "Removing a used PD from the registry should trigger an InvalidInletProtectionDomain error."
invalid_inlet_protection_domain()


@given(the_registry=preregistry())
def invalid_comm_channel_duplicate(the_registry):
    assume(the_registry.comm_channels and len(the_registry.comm_channels) > 1)

    # we pick two inlets used by different comm channels
    inlet_lists = [list(cc.inlets) for cc in the_registry.comm_channels]
    inlet1 = inlet_lists[0][0]
    inlet2 = inlet_lists[1][0]
    # then create a chimera comm channel that uses both
    new_comm_channel = CommChannel(frozenset([inlet1, inlet2]))
    the_registry.comm_channels.append(new_comm_channel)
    final_registry = the_registry.to_registry()
    # this should trigger an InvalidCommChannelDuplicate validation error

    verrs = validation_errors(final_registry)
    for verr in verrs:
        verr.format_error()
        if isinstance(verr, InvalidCommChannelDuplicate):
            return
    assert False, "Using the same inlet in two comm channels should trigger an InvalidCommChannelDuplicate error."
invalid_comm_channel_duplicate()


@given(the_registry=preregistry())
def invalid_irq_channel_duplicate(the_registry):
    assume(the_registry.irq_channels)

    # we pick an IRQ that's already in use
    used_irqs = [channel.irq for channel in the_registry.irq_channels]
    chosen_irq = used_irqs[0]
    # and an inlet not yet used for this purpose
    unused_inlets = \
      [i for i in the_registry.inlets if not (Inlet(chosen_irq, i) in the_registry.irq_channels)]
    chosen_inlet = unused_inlets[0]
    # then assign it to another inlet as well
    new_irq_channel = IRQChannel(chosen_irq, chosen_inlet)
    the_registry.irq_channels.append(new_irq_channel)
    final_registry = the_registry.to_registry()
    # this should trigger an InvalidIRQChannelDuplicate validation error

    verrs = validation_errors(final_registry)
    for verr in verrs:
        verr.format_error()
        if isinstance(verr, InvalidIRQChannelDuplicate):
            return
    assert False, "Using the same irq in two irq channels should trigger an InvalidIRQChannelDuplicate error."
invalid_irq_channel_duplicate()
