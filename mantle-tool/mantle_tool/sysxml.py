#
# Copyright 2021, Breakaway Consulting Pty. Ltd.
#
# SPDX-License-Identifier: BSD-2-Clause
#

# This file was imported from Breakaway's sel4cp_tool, and subsequently modified.
# The data layout of the SystemDescription object defined here very
# closely mirrors the hierarchical structure of the user-provided SDF. This is not
# suitable for efficient access and manipulation during the subsequent analysis and
# code generation tasks that Mantle performs, so we provide a Registry object
# in the registry module, which rearranges and organizes this data, and presents some
# convenient new abstractions.
#
# Unlike the upstream sysxml in sel4cp_tool, this version has most of the error checking
# taken out. The reason for this is twofold.
#   1. We want Mantle to work with SDF files that sel4cp itself would regard as
#      partially specified (e.g. some PDs may not have known binary paths).
#   2. The validation module provides a better, more convenient error-checking mechanism
#      for our purposes.

from dataclasses import dataclass
from pathlib import Path
# See: https://stackoverflow.com/questions/6949395/is-there-a-way-to-get-a-line-number-from-an-elementtree-element
# Force use of Python elementtree to avoid overloading
import sys
sys.modules['_elementtree'] = None  # type: ignore
import xml.etree.ElementTree as ET

from typing import Dict, Iterable, Optional, Set, Tuple

class MissingAttribute(Exception):
    def __init__(self, attribute_name: str, element: ET.Element):
        super().__init__(f"Missing attribute: {attribute_name}")
        self.attribute_name = attribute_name
        self.element = element

def checked_lookup(el: ET.Element, attr: str) -> str:
    try:
        return el.attrib[attr]
    except KeyError:
        raise MissingAttribute(attr, el)


def _check_attrs(el: ET.Element, valid_keys: Iterable[str]) -> None:
    for key in el.attrib:
        if key not in valid_keys:
            raise ValueError(f"invalid attribute '{key}'")

def str_to_bool(the_string: str) -> bool:
    if the_string.lower() == "false":
        return False
    if the_string.lower() == "true":
        return True
    raise ValueError("Invalid boolean value")

@dataclass(frozen=True, eq=True)
class PlatformDescription:
    page_sizes: Tuple[int, ...]

def default_platform_description() -> PlatformDescription:
    return PlatformDescription(page_sizes = (0x1_000, 0x200_000))

class LineNumberingParser(ET.XMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self._path = path

    def _start(self, *args, **kwargs):  # type: ignore
        element = super(self.__class__, self)._start(*args, **kwargs)
        element._path = self._path
        element._start_line_number = self.parser.CurrentLineNumber
        element._start_column_number = self.parser.CurrentColumnNumber
        element._loc_str = f"{element._path}:{element._start_line_number}.{element._start_column_number}"
        return element


@dataclass(frozen=True, eq=True)
class SysMap:
    mr: str
    vaddr: int
    perms: str
    cached: bool
    setvar_vaddr: Optional[str]


@dataclass(frozen=True, eq=True)
class SysIrq:
    irq: int
    id_: int


@dataclass(frozen=True, eq=True)
class SysSetVar:
    symbol: str
    region_paddr: Optional[str] = None
    vaddr: Optional[int] = None


@dataclass(frozen=True, eq=True)
class SysProtectionDomain:
    name: str
    priority: int
    budget: int
    period: int
    pp: bool
    maps: Tuple[SysMap, ...]
    irqs: Tuple[SysIrq, ...]
    setvars: Tuple[SysSetVar, ...]


@dataclass(frozen=True, eq=True)
class SysMemoryRegion:
    name: str
    size: int
    page_size: int
    page_count: int
    phys_addr: Optional[int]


@dataclass(frozen=True, eq=True)
class SysChannel:
    ends: tuple[tuple[str,int],...]

class SystemDescription:
    def __init__(
        self,
        memory_regions: Iterable[SysMemoryRegion],
        protection_domains: Iterable[SysProtectionDomain],
        channels: Iterable[SysChannel]
    ) -> None:
        self.memory_regions = tuple(memory_regions)
        self.protection_domains = tuple(protection_domains)
        self.channels = tuple(channels)

        if len(self.protection_domains) > 63:
            raise ValueError(f"Too many protection domains ({len(self.protection_domains)}) defined. Maximum is 63.")

        for pd in protection_domains:
            if len([pd2.name for pd2 in self.protection_domains if pd.name == pd2.name]) > 1:
                raise ValueError(f"Protection domain '{pd.name}' defined multiple times.")

        for mr in protection_domains:
            if len([mr2.name for mr2 in self.memory_regions if mr.name == mr2.name]) > 1:
                raise ValueError(f"Memory region '{mr.name}' defined multiple times.")


def xml2mr(mr_xml: ET.Element, plat_desc: PlatformDescription) -> SysMemoryRegion:
    _check_attrs(mr_xml, ("name", "size", "page_size", "phys_addr"))
    name = checked_lookup(mr_xml, "name")
    size = int(checked_lookup(mr_xml, "size"), base=0)
    page_size_str = mr_xml.attrib.get("page_size")
    page_size = min(plat_desc.page_sizes) if page_size_str is None else int(page_size_str, base=0)
    if page_size not in plat_desc.page_sizes:
        raise ValueError(f"page size 0x{page_size:x} not supported")
    if size % page_size != 0:
        raise ValueError("size is not a multiple of the page size")
    paddr_str = mr_xml.attrib.get("phys_addr")
    paddr = None if paddr_str is None else int(paddr_str, base=0)
    if paddr is not None and paddr % page_size != 0:
        raise ValueError("phys_addr is not aligned to the page size")
    page_count = size // page_size
    return SysMemoryRegion(name, size, page_size, page_count, paddr)


def xml2pd(pd_xml: ET.Element) -> SysProtectionDomain:
    _check_attrs(pd_xml, ("name", "priority", "pp", "budget", "period"))
    name = checked_lookup(pd_xml, "name")
    priority = int(pd_xml.attrib.get("priority", "0"), base=0)

    budget = int(pd_xml.attrib.get("budget", "1000"), base=0)
    period = int(pd_xml.attrib.get("period", str(budget)), base=0)

    pp = str_to_bool(pd_xml.attrib.get("pp", "false"))

    maps = []
    irqs = []
    setvars = []
    for child in pd_xml:
        try:
            if child.tag == "program_image":
                pass
            elif child.tag == "map":
                _check_attrs(child, ("mr", "vaddr", "perms", "cached", "setvar_vaddr"))
                mr = checked_lookup(child, "mr")
                vaddr = int(checked_lookup(child, "vaddr"), base=0)
                perms = child.attrib.get("perms", "rw")
                cached = str_to_bool(child.attrib.get("cached", "true"))

                setvar_vaddr = child.attrib.get("setvar_vaddr")
                if setvar_vaddr:
                    setvars.append(SysSetVar(setvar_vaddr, vaddr=vaddr))

                maps.append(SysMap(mr, vaddr, perms, cached, setvar_vaddr))
                    
            elif child.tag == "irq":
                _check_attrs(child, ("irq", "id"))
                irq = int(checked_lookup(child, "irq"), base=0)
                id_ = int(checked_lookup(child, "id"), base=0)
                irqs.append(SysIrq(irq, id_))
            elif child.tag == "setvar":
                _check_attrs(child, ("symbol", "region_paddr"))
                symbol = checked_lookup(child, "symbol")
                region_paddr = checked_lookup(child, "region_paddr")
                setvars.append(SysSetVar(symbol, region_paddr=region_paddr))
            else:
                raise ValueError(f"invalid XML element '{child.tag}': {child._loc_str}")  # type: ignore
        except ValueError as e:
            raise ValueError(f"{e} on element '{child.tag}': {child._loc_str}")  # type: ignore

    return SysProtectionDomain(name, priority, budget, period, pp, tuple(maps), tuple(irqs), tuple(setvars))


def xml2channel(ch_xml: ET.Element) -> SysChannel:
    _check_attrs(ch_xml, ())
    ends = []
    for child in ch_xml:
        try:
            if child.tag == "end":
                _check_attrs(ch_xml, ("pd", "id"))
                pd = checked_lookup(child, "pd")
                id_ = int(checked_lookup(child, "id"))
                ends.append((pd, id_))
            else:
                raise ValueError(f"invalid XML element '{child.tag}': {child._loc_str}")  # type: ignore
        except ValueError as e:
            raise ValueError(f"{e} on element '{child.tag}': {child._loc_str}")  # type: ignore

    return SysChannel(tuple(ends))



def _check_no_text(el: ET.Element) -> None:
    if not (el.text is None or el.text.strip() == ""):
        raise ValueError(f"unexpected text found in element '{el.tag}' @ {el._loc_str}")  # type: ignore
    if not (el.tail is None or el.tail.strip() == ""):
        raise ValueError(f"unexpected text found after element '{el.tag}' @ {el._loc_str}")  # type: ignore
    for child in el:
        _check_no_text(child)


def xml2system(filename: Path, plat_desc: PlatformDescription) -> SystemDescription:
    try:
        tree = ET.parse(filename, parser=LineNumberingParser(filename))
    except ET.ParseError as e:
        line, column = e.position
        raise ValueError(f"XML parsing: error @ {filename}:{line}.{column}")

    root = tree.getroot()
    memory_regions = []
    protection_domains = []
    channels = []

    # Ensure there is no non-whitespace text
    _check_no_text(root)

    for child in root:
        try:
            if child.tag == "memory_region":
                memory_regions.append(xml2mr(child, plat_desc))
            elif child.tag == "protection_domain":
                protection_domains.append(xml2pd(child))
            elif child.tag == "channel":
                channels.append(xml2channel(child))
            else:
                raise ValueError(f"invalid XML element '{child.tag}' @ {child._loc_str}")  # type: ignore
        except ValueError as e:
            raise ValueError(f"{e} on element '{child.tag}' @ {child._loc_str}")  # type: ignore
        except MissingAttribute as e:
            raise ValueError(f"missing required attribute '{e.attribute_name}' on element '{e.element.tag}': {e.element._loc_str}")  # type: ignore

    return SystemDescription(
        memory_regions=memory_regions,
        protection_domains=protection_domains,
        channels=channels,
    )
