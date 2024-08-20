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


## Usage

    ./tmconv.py examples/Grill-tag-UTM.txt --target 2 --input "eppPPPpPpppppPPPq*<>IIiIIi"


<pre>
This is a 2 state, 14 symbol machine with 1 halt state(s).
To convert to a 2 symbol machine we can expect a (125, 2) result.

Target word size: 4 symbols

	Expect	Actual
reads	28	26
writes	28	22
moves	5	5

...

TAPE: 1___1_111_11_1_1_1_1_1_11_11_1_11_111_111_111_111_11_1_1_1_1_1_111__*___1__1__1___1__1__1_1___1__1__1
</pre>

## Online interpeter

These can be run on an [online simulator](https://github.com/awmorp/turing)
* original [(2, 14) UTM](examples/Grill-Tag-2_14-UTM.txt): http://morphett.info/turing/turing.html?a2b2c66cbda6a5b2ddce0476ac390bf3
* converted [(107, 2) UTM](examples/Grill-Tag-107_2-conversion.txt): http://morphett.info/turing/turing.html?711e664dfcef99a76437560206112835
