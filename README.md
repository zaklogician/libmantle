<!--
    Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors
    SPDX-License-Identifier: CC-BY-SA-4.0
-->

<p align="center">
  <img width="150" src="/docs/logo.svg" alt="libmantle logo"></a>
</p>

<h1 align="center">libmantle</h1>

An experimental library and SDK that generates safe and efficient [austral-lang](https://austral-lang.org/)
APIs for your seL4 Core Platform projects.

1. **seL4 made simple:** libmantle builds upon the seL4 Core Platform, a
   lightweight OS framework that employs efficient and minimalistic
   abstractions.
   
2. **Safe APIs:** libmantle processes your project's System Description Files
   to generate robust and safe APIs in Austral. These APIs use linear types
   to prevent all runtime faults, and to rule out common errors such as
   neglecting to acknowledge an IRQ.

3. **FLOSS:** libmantle is free and open-source, released under the BSD
   3-clause license.

<div align="center">

**Development release**

[![license](https://img.shields.io/github/license/zaklogician/libmantle)](https://github.com/zaklogician/libmantle/blob/main/LICENSE.md)
[![austral](https://img.shields.io/badge/Austral-0.2.0-blue)](https://github.com/austral/austral/releases/tag/v0.2.0)

</div>

## About libmantle

libmantle lets you write applications running on the seL4 Core Platform using
the linearly-typed Austral programming language.

It takes your seL4 Core Platform System Description file, and uses it to
generate a safe, simple Austral API that leverages linear types to prevent all
runtime faults.

**How is libmantle different from raw seL4CP?**

The seL4 Core Platform is a fantastic foundation for building robust
applications on the seL4 microkernel, yet there is room for potential runtime
errors if its APIs are invoked incorrectly. libmantle eliminates such risks by
generating safe APIs based on the system descriptions. It only issues
capabilities to functions that your protection domain can safely invoke, thus
ruling out potential faults.

Moreover, libmantle aids you in avoiding common oversights in seL4 programming,
such as forgetting to acknowledge IRQs. With libmantle, an IRQ capability is
issued that allows for explicit acknowledgement of IRQs. Austral's linear type
system will statically check that you either acknowledged the IRQ, or
explicitly postponed acknowledging it in all code branches, making it
impossible to forget them.

**Where does libmantle generate APIs from?**

libmantle takes your System Description File, the same one used by the seL4
Core Platform SDK, as its sole input. No additional configuration or input from
the user is necessary, streamlining the process of API generation and allowing
developers to easily integrate it into existing build systems.

## Installation

`libmantle` consists of two components: an Austral library, and a Python tool
called `mantletool` that generates APIs based on seL4 Core Platform SDF files.
Please follow the steps below to install `mantletool`.

Note that the following instructions assume that you're working in a Linux,
MacOS or Windows (WSL) environment.

**Build prerequisites**

Before installing `mantletool`, make sure you have Python installed on your
system. You can verify this by typing `python --version` or
`python3 --version` into your terminal. If you do not have Python installed,
please [follow these instructions](https://www.python.org/downloads/) to
install it. You will also need `venv`, to verify that you have it, use
`python3 -m venv -h` in the terminal.

The project uses `poetry` as a build tool: it handles dependencies and
streamlines packaging, versioning, and distributing Python packages. This guide
also requires `pipx`, which will help you install and run `mantletool` in an
isolated environment, preventing conflicts between different versions of the
same dependencies.

To install `poetry`, run the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

To install `pipx`, run:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

To make sure that `poetry` and  `pipx` have been installed correctly,
restart your terminal and then run:

```bash
poetry --version
pipx --version
```

**Step 1: Cloning the repository**

Navigate to your desired directory and clone the `libmantle` repository from GitHub:

```bash
git clone https://github.com/zaklogician/libmantle.git
```

After cloning, navigate to the `libmantle/mantle-tool` directory:

```bash
cd libmantle/mantle-tool
```

**Step 2: Building the project**

With `poetry`, you can build the project. Run:

```bash
poetry build
```

This will create (among other things) a `.whl` file inside the `dist/`
directory.

**Step 3: Installing the tool**

Next, install the `.whl` file using `pipx`. Run:

```bash
pipx install dist/*.whl
```

This will install the `mantletool` CLI program.

To make sure that the installation was successful, you can run:

```bash
mantletool -h
```

If the installation was successful, you should see a help message printed to
your terminal.

**Step 4: Generating an API**

To try out the tool, you can generate an example API immediately by invoking

```bash
mantletool \
  -c examples/hello/generated.c \
  -i examples/hello/generated.aui \
  -m examples/hello/generated.aum \
  -g hello examples/hello/hello.system
```

and inspecting the `examples/hello/generated.*` files.

## Where to go from here?

* Work through the [tutorial](examples/tutorial/README.md).
* Read the [manual](docs/MANUAL.md).
* [Contribute](docs/CONTRIBUTING.md).

## License

The files in this repository are released under standard open source
licenses, identified by [SPDX license tags](https://spdx.org).

Generally, `libmantle`-specific code is released under the 3-clause BSD
license, while code derived from the seL4 Core Platform is released
under the BSD 2-clause license. See the individual file headers for
details.

The `LICENSES` directory contains the full text of all licenses that
are mentioned by files in this repository.

**IMPORTANT WARNING**

Please take note that both "libmantle" and Austral are experimental software,
and are currently under active development. They are yet to reach their version
1.0.0 release milestones. Usage of libmantle is at your own risk. We, the
developers and maintainers, disclaim any and all responsibility or liability for
any damages or losses that may result from their use.

Libmantle exists primarily as an experimental platform for investigating
linearly typed APIs. Its main purpose is to provide a sandbox for the
exploration of these concepts, rather than to serve as a reliable, stable
software solution. The Austral language itself is in its preliminary stages of
development.

Given their experimental nature and their current stage of development, neither
libmantle nor Austral are suitable for use in high-assurance systems, nor are
they certified for safety-critical applications. As such, they should NOT be
used in any circumstances where software stability and reliability are
paramount.
