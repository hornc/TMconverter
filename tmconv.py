#!/usr/bin/env python3
import argparse
import re
from math import ceil, log


ALPHABET = '_123456789ABCDEF'

# tape = 'eppPPPpPpppppPPPq*<>IIiIIi'


def key_sort(k):
    return 0 if k == '_' else ord(k)


class TM:
    def __init__(self, f):
        self.source = []
        for line in f:
            line = re.sub(r';.*', '', line)
            self.source.append(line.strip().split())
        self.count_current()
        self.rules = set()

    def count_current(self):
        self.state = set()
        self.symbol = set()
        self.halt = set()
        self.reads = set()
        self.writes = set()
        self.moves = set()
        for row in self.source:
            self.state.add(row[0])
            self.symbol.add(row[1])
            self.symbol.add(row[2])
            trans = row[4]
            if trans.startswith('halt'):
                self.halt.add(trans)
            self.writes.add(' '.join(row[2:5]))
        print('reads', self.reads)

        self.state.discard('*')
        self.symbol.discard('*')
        self.symbol = list(self.symbol)
        self.symbol.sort(key=key_sort)
        for row in self.source:
            move = ' '.join(row[3:5])
            trans = row[4]
            if trans == '*':
                for state in self.state:
                    self.moves.add(move.replace('*', state))
            else:
                self.moves.add(move)
            read = ' '.join(row[:2])
            if read.startswith('*'):
                for state in self.state:
                    self.reads.add(read.replace('*', state))
            else:
                self.reads.add(' '.join(row[:2]))
        return self.stats()

    def stats(self):
        return len(self.state), len(self.symbol), len(self.halt)

    def classes(self):
        reads = len(self.reads)
        return reads, len(self.writes), len(self.moves)

    def makedict(self, target=2):
        print(f'Symbols: {self.symbol}')
        w = ceil(log(len(self.symbol), target))
        d = {v: bin(i)[2:].zfill(w).replace('0', '_') for i,v in enumerate(self.symbol)}
        #print(d)
        return d

    def rev_trans(self, tape):
        tape = tape.replace('0', '_').replace(' ', '_').replace('*', '')
        out = ''
        d = self.makedict(2)
        rd = {v: k for k,v in d.items()}
        print(rd)
        while tape:
            w = tape[:4]
            out += rd[w]
            tape = tape[4:]
        return out


    def translate(self, tape):
        out = ''
        d = self.makedict(2)
        for c in tape:
            if c == '*':
                out += c
            else:
                a = d[c]
                assert len(a) == 4
                out += a
        return out

    def addrule(self, rule:list):
        assert len(rule) == 5
        assert '*' not in rule[0]
        assert '*' not in rule[4]
        self.rules.add(' '.join(rule))

    def convert(self, target=2):
        w = ceil(log(len(self.symbol), target))
        d = self.makedict(target)
        self.addrule(['0', '0', '_', '*', '0'])
        for read in self.reads:
            read = read.split()
            s = read[-1]
            word = d[s]
            ostate = read[0] 
            for i in range(w - 1):
                c = '.' if i == 0 else '.' + word[:i]
                self.addrule([(ostate + c).strip('.'), '_', '*', 'r', ostate + c + '_'])
                self.addrule([(ostate + c).strip('.'), '1', '*', 'r', ostate + c + '1'])

        for rule in self.source:
            ostate = rule[0]
            s = rule[1]
            word = d[s]
            owrite = rule[2]
            write = d[owrite]
            nstate = rule[4]
            ndir = rule[3]
            if ostate == '*':
                ostate = ('0', '1')

            for os in ostate:
                if nstate == '*':
                    ns = os
                else:
                    ns = nstate
                assert os != '*'
                r = [os + '.' + word[:-1], word[-1], write[-1], 'l', ns + f'.{owrite}{ndir}1']
                self.addrule(r)

        for write in self.writes:
            write = write.split()
            nstate = write[-1]
            ndir = write[1]
            s = write[0]
            word = d[s]
            for i,c in enumerate(word[1:]):
                if i == 2:
                    nlabel = f'{nstate}{ndir}'
                else:
                    nlabel = nstate + f'.{s}{ndir}{i+2}'
                if 'halt' in nlabel:
                    nlabel = 'halt'
                ns = ('0', '1') if nstate == '*' else nstate
                for n in ns:
                    self.addrule([n + f'.{s}{ndir}{i+1}', '*', word[-(i+2)], 'l', nlabel.replace('*', n)])

        for move in self.moves:
            move = move.split()
            ndir, nstate = move
            if ndir == 'l':
                m = 4
            else:
                m = 6 
            for i in range(1, m):
                clabel = nstate + ndir + ('' if i == 1 else str(i))
                nlabel = nstate if i == (m-1) else (nstate + ndir + str(i+1))
                self.addrule([clabel, '*', '*', ndir, nlabel])
            
        print('\n'.join(self.rules))


def conv(n, m, h=1, t=2):
    # n states, m symbols, assumes a strongly universal UTM with 1 halt state
    r = n * m  # assume maximal read cases
    w = ceil(log(m, t))  # word width of orig. symbols in new symbols
    return r * (w + 2*(w - 1)) - h * (w - 1)


def main():
    parser = argparse.ArgumentParser(description='Turing state machine converter')
    parser.add_argument('file', help='Source Turing machine specification', type=argparse.FileType('r'))
    parser.add_argument('--target', '-t', help='Target number of symbols to convert to', type=int, default=2)
    parser.add_argument('--input', '-i', help='Input starting string')
    parser.add_argument('--conv', '-c', help='Convert back tape')
    args = parser.parse_args()

    f = args.file
    target = args.target
    directions = 2  # 1d tape has two directions, l and r

    orig = TM(f)
    state, symbol, halt = orig.stats() 
    expected_states = conv(state, symbol, h=halt, t=target)
    reads, writes, moves = orig.classes()
    print(f'This is a {state} state, {symbol} symbol machine with {halt} halt state(s).')
    print(f'To convert to a {target} symbol machine we can exepct a ({expected_states}, {target}) result.')

    w = ceil(log(symbol, target))
    print(f'\nTarget word size: {w} symbols')

    e_reads = state * symbol
    e_writes = state * symbol  # we probably expect less?
    e_moves = directions * state + halt
    table = [
              ['', 'Expected', 'Actual'],
              ['reads', e_reads, reads],
              ['writes', e_writes, writes],
              ['moves', e_moves, moves],
            ]
    print()
    for row in table:
        print('\t'.join([str(v) for v in row]))

    # Do the conversion...
    print('DICT', orig.makedict(target))
    orig.convert(target)

    if args.input:
        print('TAPE', orig.translate(args.input))

    if args.conv:
        print('CONVERT BACK', orig.rev_trans(args.conv))


if __name__ == '__main__':
    main()
