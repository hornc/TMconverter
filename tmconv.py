#!/usr/bin/env python3
import argparse
import re
from math import ceil, log


ALPHABET = '_123456789ABCDEF'
NODELIST = 'tm_nodelist.csv'
EDGELIST = 'tm_edgelist.csv'

# tape = 'eppPPPpPpppppPPPq*<>IIiIIi'


def key_sort(k):
    return 0 if k == '_' else ord(k)


class TM:
    def __init__(self, f):
        self.source = []
        for line in f:
            line = re.sub(r';.*', '', line).strip()
            if line:
               self.source.append(line.split())
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

        self.state.discard('*')
        self.symbol.discard('*')
        self.symbol.discard('0')
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
        #print(f'Symbols: {self.symbol}')
        w = ceil(log(len(self.symbol), target))
        d = {v: bin(i)[2:].zfill(w).replace('0', '_') for i,v in enumerate(self.symbol)}
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
        assert 'halt' not in rule[0]
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
                    ns = f'{os}.{owrite}{ndir}1'
                elif 'halt' in nstate:
                    ns = 'halt'
                else:
                    ns = f'{nstate}.{owrite}{ndir}1'
                assert os != '*'
                r = [os + '.' + word[:-1], word[-1], write[-1], 'l', ns]
                self.addrule(r)

        for write in self.writes:
            write = write.split()
            nstate = write[-1]
            if 'halt' in nstate:
                continue
            ndir = write[1]
            s = write[0]
            word = d[s]
            for i,c in enumerate(word[1:]):
                if i == 2:
                    nlabel = f'{nstate}{ndir}'
                else:
                    nlabel = nstate + f'.{s}{ndir}{i+2}'
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
                if 'halt' in clabel:
                    continue
                nlabel = nstate if i == (m-1) else (nstate + ndir + str(i+1))
                self.addrule([clabel, '*', '*', ndir, nlabel])
        self.rules = list(self.rules)
        self.rules.sort()
        print('\n'.join(self.rules))

    def graph(self, fmt):
        """
        Convert machine into a graph format fmt
        1: basic Gephi CSV
        """
        # Nodes
        # Id,Label
        nodes = {'halt': '0'}
        with open(NODELIST, 'w') as f:
            print(f'Writing Nodes to {NODELIST}...')
            f.write(','.join(['Id', 'Label']) + '\n')
            f.write(f'0,"halt"\n')  # HALT at id = 0
            for i, state in enumerate(self.state, 1):
                f.write(','.join([str(i), f'"{state}"']) + '\n')
                nodes[state] = str(i)

        # Edges
        # Source,Target | Weight , Type
        with open(EDGELIST, 'w') as f:
            print(f'Writing Edges to {EDGELIST}...')
            f.write(','.join(['Source', 'Target', 'Label']) + '\n')
            for transition in self.source:
                #print(transition)
                s, read, write, dir_, dest = transition
                edge_label = f'{read}:{write}:{dir_}'
                if s == '*':
                    for n in self.state:
                        if dest == '*':
                            target = nodes[n]
                        else:
                            target = nodes[dest]
                        f.write(','.join([nodes[n], target, edge_label]) + '\n')
                else:
                    f.write(','.join([nodes[s], nodes[dest], edge_label]) + '\n')



def conv(n, m, h=1, t=2):
    # n states, m symbols, assumes a strongly universal UTM with 1 halt state
    r = n * m  # assume maximal read cases
    w = ceil(log(m, t))  # word width of orig. symbols in new symbols
    return r + ((n * m) - h) * (w - 1) + w * 2 * n


def main():
    parser = argparse.ArgumentParser(description='Turing state machine converter')
    parser.add_argument('file', help='Source Turing machine specification', type=argparse.FileType('r'))
    parser.add_argument('--target', '-t', help='Target number of symbols to convert to', type=int, default=2)
    parser.add_argument('--input', '-i', help='Input starting string')
    parser.add_argument('--conv', '-c', help='Convert back tape')
    parser.add_argument('--graph', '-g', help='Convert machine to Gephi graph format (mode=1, 2, or 3)', type=int)
    args = parser.parse_args()

    f = args.file
    target = args.target
    directions = 2  # 1d tape has two directions, l and r

    orig = TM(f)
    state, symbol, halt = orig.stats() 
    expected_states = conv(state, symbol, h=halt, t=target)
    reads, writes, moves = orig.classes()
    print(f'This is a {state} state, {symbol} symbol machine with {halt} halt state(s).')
    print(f'To convert to a {target} symbol machine we can expect a ({expected_states}, {target}) result.')

    w = ceil(log(symbol, target))
    print(f'\nTarget word size: {w} symbols')

    e_reads = state * symbol
    e_writes = state * symbol  # we probably expect less?
    e_moves = directions * state + halt
    table = [
              ['', 'Expect', 'Actual'],
              ['reads', e_reads, reads],
              ['writes', e_writes, writes],
              ['moves', e_moves, moves],
            ]
    print()
    for row in table:
        print('\t'.join([str(v) for v in row]))
    print()

    if fmt := args.graph:
        print(f'Output machine as graph format {fmt}...')
        orig.graph(fmt)

    # Do the conversion...
    if symbol != target:
        orig.convert(target)

    if args.input:
        print('\nTAPE:', orig.translate(args.input))

    if args.conv:
        print('CONVERT BACK:', orig.rev_trans(args.conv))


if __name__ == '__main__':
    main()
