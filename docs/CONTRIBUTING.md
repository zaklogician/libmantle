<!-- Copyright 2023, COMAS (ABN 11 932 720 318) and the project contributors -->
<!-- SPDX-License-Identifier: BSD-3-Clause -->

Contribute to libmantle by:
* creating an issue on the Github issue tracker; or
* submitting a pull request against the `develop` branch of this repository.

## Coding style

The coding style used in this repository is standard PEP8 for Python code,
and the most current [Austral specification guidelines](https://austral-lang.org/spec/)
for Austral code.

There is currently no CI/CD in this repository, so we ask that you manually
run `autopep8` to auto-format any source files in your pull requests.

We use `mypy` for static analysis of Python code, and will not accept any
code (apart from unit tests) without explicit type annotations backed by
`mypy`.

## DCO

You should indicate acceptance of the [Developer Certificate of
Origin](https://developercertificate.org/)_ by appending a
`Signed-off-by: Your Name <example@domain.com>` line to each of your git commit
messaged (see `git commit -s`).
