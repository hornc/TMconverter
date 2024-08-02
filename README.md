# TMconverter
converts n state, m symbol Turing machines to more-state, less-symbol versions


## Purpose
Using the format used by http://morphett.info/turing/turing.html , this tool converts an n-state, m-symbol Turing machine
into a 2-symbol equivalent.

Main target: the (2, 14) [Grill tag UTM](https://esolangs.org/wiki/Grill_Tag#Turing_machine_implementation)

## Goals

* 2-symbol conversion (DONE)
* Static Analysis of the given Turing machine and provide an indication of utilised states and complexity
* Visual state diagram output
