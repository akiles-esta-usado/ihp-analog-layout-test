# IHP Analog Design Example

This work is based on Felipe Torres examples from the CANELOS2024 workshop

## Usage

We use a `Makefile` to hold multiple rules that performs basic operations, like opening a program
or performing lvs.

The variable `TOP` points to a module that contains the schematics, layout, and each file related to a specific section of the design
Some of the rules requires it, like lvs or drc. But some of them just open the program

~~~bash
make TOP=inv klayout

make TOP=inv xschem

make TOP=inv klayout-drc

make TOP=inv klayout-lvs

make klayout

make xschem
~~~

## Troubleshoot

- **Modules should not contain '-', only '_'**