#
# Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
# SPDX-License-Identifier: BSD-3-Clause
#

"""validation.py

This module provides methods for validating Registry objects, and helper
classes for producing validation errors.

"""

from types import MappingProxyType
from typing import (Union, Optional)
from dataclasses import dataclass

from mantle_tool.registry import (
    ProtectionDomain, Inlet, CommChannel, IRQChannel, MappedMemoryRegion, Registry)


class InvalidProtectionDomainName:
    """
    Represents an error case where a protection domain's name contains unsupported characters.

    While certain unsupported names might work in raw sel4cp, Mantle only supports letters of
    the English alphabet, numbers and underscores in the names of protection domains. This makes
    code generation more reliable, and the resulting names in the Austral code more predictable.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_protection_domain : ProtectionDomain
        The ProtectionDomain that has the invalid name.
    invalid_chars : list[str]
        The unsupported characters that occur in the name of the given ProtectionDomain.


    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_protection_domain: ProtectionDomain, invalid_characters: list[str]) -> None:
        self.originating_registry = originating_registry
        self.invalid_protection_domain = invalid_protection_domain
        self.invalid_characters = invalid_characters

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        return "Protection domain has invalid name: '{name}'.".format(name=self.invalid_protection_domain.name)

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
            "The name of this protection domain contains some characters ({chars}) that are not supported by Mantle.".format(
                chars=self.invalid_characters)
        hint: str = \
            "Hint: You can use letters of the English alphabet, numbers and underscores. Start with a letter."
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidMappedMemoryRegionName:
    """
    Represents an error case where a mapped memory region's name contains unsupported characters.

    While certain unsupported names might work in raw sel4cp, Mantle only supports letters of
    the English alphabet, numbers and underscores in the names of protection domains. This makes
    code generation more reliable, and the resulting names in the Austral code more predictable.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_memory_region : MappedMemoryRegion
        The MappedMemoryRegion that has the invalid name.
    invalid_chars : list[str]
        The unsupported characters that occur in the name of the given MappedMemoryRegion.


    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_memory_region: MappedMemoryRegion, invalid_characters: list[str]) -> None:
        self.originating_registry = originating_registry
        self.invalid_memory_region = invalid_memory_region
        self.invalid_characters = invalid_characters

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        return "Mapped memory region has invalid name: '{name}'.".format(name=self.invalid_memory_region.name)

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
            "The name of this memory region contains some characters ({chars}) that are not supported by Mantle.".format(
                chars=self.invalid_characters)
        hint: str = \
            "Hint: You can use letters of the English alphabet, numbers and underscores. Start with a letter."
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidMappedMemoryRegionPatchSymbol:
    """
    Represents an error case where a mapped memory region's patch symbol contains unsupported characters.

    While certain unsupported names might work in raw sel4cp, Mantle only supports letters of
    the English alphabet, numbers and underscores in the names of protection domains. This makes
    code generation more reliable, and the resulting names in the Austral code more predictable.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_protection_domain: ProtectionDomain
        The ProtectionDomain in which a memory region has an invalid patch symbol name
    invalid_memory_region : MappedMemoryRegion
        The MappedMemoryRegion that has the invalid patch symbol in the given ProtectionDomain.
    invalid_chars : list[str]
        The unsupported characters that occur in the name of the given MappedMemoryRegion.


    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_protection_domain: ProtectionDomain, invalid_memory_region: MappedMemoryRegion, invalid_characters: list[str]) -> None:
        self.originating_registry = originating_registry
        self.invalid_protection_domain = invalid_protection_domain
        self.invalid_memory_region = invalid_memory_region
        self.invalid_characters = invalid_characters

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        return "Mapped memory region has invalid patch symbol: '{ps}' in '{pd}'.".format(ps=self.invalid_memory_region.patch_symbol, pd=self.invalid_protection_domain.name)

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
            "The setvar_vaddr of this memory region contains characters ({chars}) that are not supported by Mantle.".format(
                chars=self.invalid_characters)
        hint: str = \
            "Hint: You can use letters of the English alphabet, numbers and underscores. Start with a letter."
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidInletProtectionDomain:
    """
    Represents an error case where an inlet's protection domain does not exist in the Registry.

    This can happen e.g. if the user declared a channel end with pd attribute containing a
    name that has no matching protection_domain element.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_inlet : Inlet
        The Inlet that has the invalid number.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_inlet: Inlet) -> None:
        self.originating_registry = originating_registry
        self.invalid_inlet = invalid_inlet

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_inlet.protection_domain.name
        number = self.invalid_inlet.number
        return "Inlet's protection domain does not exist: ('{name}', {number}).".format(name=name, number=number)

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
            "The protection domain of this inlet has not been defined in this registry."

        # suggest 3 names of similar length (potential typos)
        suggestions: list[str] = \
            [pd.name for pd in self.originating_registry.protection_domains]
        suggestions.sort(key=lambda x: abs(
            len(x) - len(self.invalid_inlet.protection_domain.name)))
        hint: str = \
            "Hint: Did you mean one of %s?" % suggestions[:3]

        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidInletNumber:
    """
    Represents an error case where an inlet's number is out of the supported range.

    This can happen e.g. if the user declared a channel end with id attribute larger than 63
    in the SDF.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_inlet : Inlet
        The Inlet that has the invalid number.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_inlet: Inlet) -> None:
        self.originating_registry = originating_registry
        self.invalid_inlet = invalid_inlet

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_inlet.protection_domain.name
        number = self.invalid_inlet.number
        return "Inlet's number is invalid: ('{name}', {number}).".format(name=name, number=number)

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
            "The inlet number (channel id) of this inlet falls outside the range supported by seL4CP and Mantle."
        hint: str = \
            "Hint: The number should belong to the range 0..63, inclusive."
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidCommChannelCount:
    """
    Represents an error case where some communication channel does not have exactly two inlets.

    This can happen e.g. if the user declared too many end elements inside an SDF's
    channel element.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_comm_channel : CommChannel
        The CommChannel that has the invalid number of inlets.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_comm_channel: CommChannel) -> None:
        self.originating_registry = originating_registry
        self.invalid_comm_channel = invalid_comm_channel

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        issue = "too many"
        if len(self.invalid_comm_channel.inlets) < 2:
            issue = "too few"
        inlets: str = str([(i.protection_domain.name, i.number)
                          for i in self.invalid_comm_channel.inlets])
        return "Comm channel has {issue} inlets: {inlets}.".format(issue=issue, inlets=inlets)

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
        issue: str = "too many"
        if len(self.invalid_comm_channel.inlets) < 2:
            issue = "too few"
        description: str = \
            "This communication channel connects {issue} protection domains.".format(
                issue=issue)
        hint: str = \
            "Hint: A communication channel should have exactly 2 inlets."
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidCommChannelInlet:
    """
    Represents an error case where a communication channel's inlet does not exist in the registry.

    This can happen e.g. if the user mistyped the name of the protection domain in an SDF's
    channel element.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_comm_channel : CommChannel
        The CommChannel that has the invalid inlet.
    invalid_inlet : Inlet
        The inlet of the given CommChannel that the error pertains to.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_comm_channel: CommChannel, invalid_inlet: Inlet) -> None:
        self.originating_registry = originating_registry
        self.invalid_comm_channel = invalid_comm_channel
        self.invalid_inlet = invalid_inlet

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_inlet.protection_domain.name
        number = self.invalid_inlet.number
        inlets: str = str(["(%s,%s)" % (i.protection_domain.name, i.number)
                          for i in self.invalid_comm_channel.inlets])
        return "Comm channel's inlet does not exist: ('{name}', {number}) in {inlets}.".format(name=name, number=number, inlets=inlets)

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
            "One of the inlets of this communication channel has not been defined in this registry."

        # suggest 3 names of similar length (potential typos)
        suggestions: list[str] = \
            [pd.name for pd in self.originating_registry.protection_domains]
        suggestions.sort(key=lambda x: abs(
            len(x) - len(self.invalid_inlet.protection_domain.name)))
        hint: str = \
            "Hint: Did you mean one of %s?" % suggestions[:3]

        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidCommChannelDuplicate:
    """
    Represents an error case where two communication channels share the same inlet in the registry.

    This can happen e.g. if the user copy-pasted a channel element, and forgot to change one of the
    channel ids in the SDF.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_comm_channel : CommChannel
        The CommChannel that has the invalid duplicate inlet.
    invalid_inlet : Inlet
        The inlet of the given CommChannel that the error pertains to.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_comm_channel: CommChannel, invalid_inlet: Inlet) -> None:
        self.originating_registry = originating_registry
        self.invalid_comm_channel = invalid_comm_channel
        self.invalid_inlet = invalid_inlet

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_inlet.protection_domain.name
        number = self.invalid_inlet.number
        inlets: str = str([(i.protection_domain.name, i.number)
                          for i in self.invalid_comm_channel.inlets])
        return "Comm channel targets an inlet already in use: ('{name}', {number}) in {inlets}.".format(name=name, number=number, inlets=inlets)

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
            "This communication channel shares one of its inlets with another communication channel."

        # suggest an unoccupied inlet number
        occupied: list[int] = \
            [i.number for i in self.originating_registry.inlets if i.protection_domain ==
                self.invalid_inlet.protection_domain]
        min_occupied: int = min(occupied + [63])
        max_occupied: int = max(occupied + [0])
        name = self.invalid_inlet.protection_domain.name
        hint: str = \
            "Hint: Use 'id=' to move this channel to another inlet of '{name}'.".format(
                name=name)
        if min_occupied > 0:
            free_inlet = min_occupied - 1
            hint = \
                "Hint: Use 'id=' to move this channel to inlet {inlet} of '{name}'.".format(
                    name=name, inlet=free_inlet)
        if max_occupied < 63:
            free_inlet = max_occupied + 1
            hint = \
                "Hint: Use 'id=' to move this channel to inlet {inlet} of '{name}'.".format(
                    name=name, inlet=free_inlet)
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidIRQChannelInlet:
    """
    Represents an error case where an IRQ channel's inlet does not exist in the registry.

    This usually does not happen in a Registry parsed from a user-provided SDF, as the SDF
    provides no mechanism for declaring IRQ channels outside a protection_domain element.
    However, it may happen in registries constructed by other means, such as directly from
    Python code.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_irq_channel : IRQChannel
        The IRQChannel that has the invalid inlet.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_irq_channel: IRQChannel) -> None:
        self.originating_registry = originating_registry
        self.invalid_irq_channel = invalid_irq_channel

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_irq_channel.inlet.protection_domain.name
        number = str(self.invalid_irq_channel.inlet.number)
        inlet = self.invalid_irq_channel.inlet
        irq: str = str(self.invalid_irq_channel.irq)
        return "IRQ channel's inlet does not exist: ('{name}', {number}) for IRQ {irq}.".format(name=name, number=number, irq=irq)

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
            "The inlet of this IRQ channel has not been defined in this registry."

        # suggest 3 names of similar length (potential typos)
        suggestions: list[str] = \
            [pd.name for pd in self.originating_registry.protection_domains]
        inlet = self.invalid_irq_channel.inlet
        suggestions.sort(key=lambda x: abs(
            len(x) - len(inlet.protection_domain.name)))
        hint: str = \
            "Hint: Did you mean one of %s?" % suggestions[:3]

        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidIRQChannelDuplicate:
    """
    Represents an error case where an IRQ number occurs as the target of more than one IRQ
    channel.

    This happens e.g. if the user specified the same irq number as an irq child of two
    different protection_domain elements of the SDF.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_irq_channel : IRQChannel
        The IRQChannel that has the invalid shared number.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_irq_channel: IRQChannel) -> None:
        self.originating_registry = originating_registry
        self.invalid_irq_channel = invalid_irq_channel

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_irq_channel.inlet.protection_domain.name
        number = str(self.invalid_irq_channel.inlet.number)
        inlet = self.invalid_irq_channel.inlet
        irq: str = str(self.invalid_irq_channel.irq)
        return "IRQ channel targets an IRQ already in use: ('{name}', {number}) for IRQ {irq}.".format(name=name, number=number, irq=irq)

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
            "This IRQ channel targets an IRQ number which is already set up to notify another inlet."

        # suggest irqs to remove
        clashes: list[IRQChannel] = \
            [ic for ic in self.originating_registry.irq_channels if ic.irq ==
                self.invalid_irq_channel.irq]
        suggestions: list[tuple[str, int]] = \
            [(ic.inlet.protection_domain.name, ic.inlet.number)
             for ic in clashes]
        hint: str = \
            "Hint: Remove this irq from one of the following inlets: %s." % suggestions[:2]
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidCommAndIRQClash:
    """
    Represents an error case where a communication channel and an IRQ channel occupy
    the same inlet of a protection domain.

    While this works in raw sel4cp, Mantle cannot support it: a protection domain
    cannot tell, based on the notification received, whether the other PD or the IRQ
    triggered the notification. AS such it's not possible to statically determine
    whether the IRQ should be acknowledged or not.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_comm_channel : CommChannel
        The CommChannel that shares an inlet with the given IRQChannel.
    invalid_irq_channel : IRQChannel
        The IRQChannel that shares an inlet with the given CommChannel.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_comm_channel: CommChannel, invalid_irq_channel: IRQChannel) -> None:
        self.originating_registry = originating_registry
        self.invalid_comm_channel = invalid_comm_channel
        self.invalid_irq_channel = invalid_irq_channel

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        inlet = self.invalid_irq_channel.inlet
        name = inlet.protection_domain.name
        number = str(inlet.number)
        irq: str = str(self.invalid_irq_channel.irq)
        inlets: str = str([(i.protection_domain.name, i.number)
                          for i in self.invalid_comm_channel.inlets])
        return "Comm and IRQ channel occupy same inlet: ('{name}', {number}) for IRQ {irq} and {inlets}.".format(name=name, number=number, irq=irq, inlets=inlets)

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
            "A communication channel and an IRQ channel notify the same inlet. This is not supported by Mantle."
        inlet = self.invalid_irq_channel.inlet
        hint: str = \
            "Hint: Use 'id=' to set this IRQ to notify a different inlet of '{name}'.".format(
                name=inlet.protection_domain.name)
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


class InvalidProtectionDomainPriority:
    """
    Represents an error case where a ProtectionDomain has no priority setting, or has
    a priority setting but it lies outside the supported range.

    Attributes:
    ----------
    originating_registry : Registry
        The registry from which the error originated.
    invalid_protection_domain : ProtectionDomain
        The ProtectionDomain with the invalid priority.

    Methods:
    -------
    format_short_error() -> str:
        Generates a concise, human-readable summary of the error.
    format_error() -> str:
        Generates a detailed, human-readable error message with troubleshooting hints.
    """

    def __init__(self, originating_registry: Registry, invalid_protection_domain: ProtectionDomain) -> None:
        self.originating_registry = originating_registry
        self.invalid_protection_domain = invalid_protection_domain

    def format_short_error(self) -> str:
        """
        A concise, human-readable summary of the error.

        Returns:
        -------
        str
            The formatted error message.
        """
        name = self.invalid_protection_domain.name
        return "Protection domain has invalid priority: '{name}'.".format(name=name)

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
            "This protection domain has its priority set to a value that is not supported by Mantle."
        hint: str = \
            "Hint: Set the priority using 'priority=' to a value in the range 0..254 (inclusive)."
        location: str = \
            "Location: {provenance}".format(
                provenance=self.originating_registry.description)
        error: str = \
            "{title}\n\n{desc}\n{hint}\n{location}\n".format(
                title=title, desc=description, hint=hint, location=location)
        return error


ValidationError = \
    Union[InvalidProtectionDomainName, InvalidMappedMemoryRegionName, InvalidMappedMemoryRegionPatchSymbol, InvalidInletProtectionDomain, InvalidInletNumber, InvalidCommChannelCount,
          InvalidCommChannelInlet, InvalidCommChannelDuplicate, InvalidIRQChannelInlet, InvalidIRQChannelDuplicate, InvalidCommAndIRQClash, InvalidProtectionDomainPriority]


def name_validator(name: str) -> list[str]:
    if len(name) < 1:
        return [' ']
    violating_characters: list[str] = [
        c for c in name if (not c.isalnum()) and c != '_']
    if not name[0].isalpha():
        violating_characters = [name[0]] + violating_characters
    return violating_characters


def validation_errors(registry: Registry) -> list[ValidationError]:
    """
    Validate a Registry object against the Mantle requirements, and return a list of any validation errors.

    This function checks a variety of conditions on the given Registry object to ensure it is valid.
    The conditions include:
    1. Protection domain names should only contain alphanumeric characters and underscores.
    2. Protection domains should have priority settings in the valid range (0 to 254, inclusive).
    3. Inlets should belong to a defined protection domain and have a number in the range 0 to 63.
    4. Communication channels should have exactly 2 inlets.
    5. All IRQ channels should have a defined inlet.
    6. No inlet should belong to both an IRQ channel and a communication channel.

    Currently, we perform no checks for overlapping memory regions. The sel4cp_tool can report
    these while building the project, and they do not affect code generation in any way.

    If any of these conditions are not met, a ValidationError is added to the returned list with
    details of the violation.

    Parameters
    ----------
    registry : Registry
        The Registry object to validate.

    Returns
    -------
    list[ValidationError]
        A list of all validation errors found in the registry. Empty if the registry is valid.
    """
    all_violations: list[ValidationError] = list()

    # 1. check for invalid pd and mr names
    violating_characters: list[str] = list()
    for pd in registry.protection_domains:
        violating_characters = name_validator(pd.name)
        if violating_characters:
            pd_name_violation = InvalidProtectionDomainName(
                registry, pd, violating_characters)
            all_violations.append(pd_name_violation)

    for mr in registry.mapped_memory_regions:
        violating_characters = name_validator(mr.name)
        if violating_characters:
            mr_name_violation = InvalidMappedMemoryRegionName(
                registry, mr, violating_characters)
            all_violations.append(mr_name_violation)
        if mr.patch_symbol:
            violating_characters = name_validator(mr.patch_symbol)
            if violating_characters:
                mr_patch_symbol_violation = InvalidMappedMemoryRegionPatchSymbol(
                    registry, mr.protection_domain, mr, violating_characters)
                all_violations.append(mr_patch_symbol_violation)

    # 2. check for pds with invalid priority settings
    pds_without_priority = \
        [pd for pd in registry.protection_domains if not registry.priority_by_protection_domain[pd]
         or registry.priority_by_protection_domain[pd] > 254
         or registry.priority_by_protection_domain[pd] < 0]
    pd_priority_violations = \
        [InvalidProtectionDomainPriority(registry, pd)
         for pd in pds_without_priority]
    all_violations.extend(pd_priority_violations)

    # 3. check for invalid inlets
    inlets_with_invalid_pd = \
        [i for i in registry.inlets if not (
            i.protection_domain in registry.protection_domains)]
    inlet_pd_violations = \
        [InvalidInletProtectionDomain(registry, i)
         for i in inlets_with_invalid_pd]
    all_violations.extend(inlet_pd_violations)

    inlets_with_invalid_number = \
        [i for i in registry.inlets if i.number < 0 or i.number > 63]
    inlet_number_violations = \
        [InvalidInletNumber(registry, i) for i in inlets_with_invalid_number]
    all_violations.extend(inlet_number_violations)

    # 4. check for invalid comm channels
    comms_with_invalid_count = \
        [c for c in registry.comm_channels if len(c.inlets) != 2]
    comm_count_violations = \
        [InvalidCommChannelCount(registry, c)
         for c in comms_with_invalid_count]
    all_violations.extend(comm_count_violations)

    for c in registry.comm_channels:
        comm_invalid_inlets = \
            [i for i in c.inlets if not (i in registry.inlets)]
        comm_inlet_violations = \
            [InvalidCommChannelInlet(registry, c, i)
             for i in comm_invalid_inlets]
        all_violations.extend(comm_inlet_violations)

        for i in c.inlets:
            comm_invalid_duplicates = \
                [cc for cc in registry.comm_channels if i in cc.inlets and cc != c]
            if comm_invalid_duplicates:
                all_violations.append(
                    InvalidCommChannelDuplicate(registry, c, i))

    # 5. check for invalid IRQ channels
    irq_channel_invalid_inlets = \
        [ic for ic in registry.irq_channels if not (
            ic.inlet in registry.inlets)]
    irq_channel_inlet_violations = \
        [InvalidIRQChannelInlet(registry, ic)
         for ic in irq_channel_invalid_inlets]
    all_violations.extend(irq_channel_inlet_violations)

    for ic in registry.irq_channels:
        irq_channel_invalid_duplicates = \
            [i for i in registry.irq_channels if i.irq == ic.irq and i != ic]
        if irq_channel_invalid_duplicates:
            all_violations.append(InvalidIRQChannelDuplicate(registry, ic))

    # 6. check for IRQ/comm channel clashes
    for ic in registry.irq_channels:
        clashing_inlets = \
            [(c, i) for c in registry.comm_channels for i in c.inlets if i == ic.inlet]
        irq_comm_clash_violations = \
            [InvalidCommAndIRQClash(registry, c, ic)
             for (c, i) in clashing_inlets]
        all_violations.extend(irq_comm_clash_violations)

    return all_violations
