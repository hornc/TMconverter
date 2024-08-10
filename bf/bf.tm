; bf interpreter as a Turing machine, to be run on the simulator at
; http://morphett.info/turing/turing.html
; or equivalent

; Symbol encoding:
;	_	> 	< 	+ 	- 	. 	, 	[ 
;	0	1 	2 	3 	4 	5 	6 	7 

; Start in state 0
; move left to set up the begining of the tape (runs right to left from just before the bf code)
0 * * l m1

; This is the tape we are setting up:
; abcXP abcXP abcXP ]]]X<
;  write 2 symbol to mark the start of the tape
m1 _ < l extendtape

extendtape _ _ l x1
x1 _ _ l x2
x2 _ _ l x3
x3 _ _ l x4
x4 _ > r return  ; write current data pointer and return to code

return * * r r1
r1 * * r r2
r2 * * r r3
r3 * * r r4
r4 < < r c0
r4 _ _ r return

; running, move to current PC
c0 _ _ r codefound
codefound _ _ r c1
codefound > _ r command
c1 * * r codefound


; commands
command + + r incadv
command > > r fwdadv  ; advance the pointer on a advance dp command
command - - r decadv
command < < r retadv
command [ [ r braadv
command _ _ l endret  ; on ], retreat the IP, in case we need to repeat left


incadv _ > l inc1  ; set PC to next instruction
fwdadv _ > l fwd1
decadv _ > l dec1
retadv _ > l ret1
braadv _ > l bra1  ; bracket test
endret _ > l end1  ; end bracket test

; move leftwards through the program to start of tape
inc1 * * l inc2
inc2 _ _ l inc1
inc2 < < l incfinddp


incfinddp _ _ l ifd1
ifd1 * * l ifd2
ifd2 * * l ifd3
ifd3 * * l ifd4

ifd4 > > r doinc ; found current cell to increment
ifd4 _ _ l incfinddp  ; keep searching left

doinc * * r di1
di1 * * r incc


; inc c pos
incc _ > r r3
incc > < r r3
incc < + r r3
incc + - r r3
incc - . r r3
incc . , r r3
incc , [ r r3
incc [ _ l incb  ; carry add

; inc b pos
incb _ > r r2
incb > < r r2
incb < + r r2
incb + - r r2
incb - . r r2
incb . , r r2
incb , [ r r2
incb [ _ l inca  ; carry add


; > move datapointer forward 1
fwd1 * * l fwd2
fwd2 _ _ l fwd1
fwd2 < < l fwdfinddp   ; locate the start of the tape


fwdfinddp _ _ l ffd1
ffd1 * * l ffd2
ffd2 * * l ffd3
ffd3 * * l ffd4

ffd4 > _ l extendtape  ; found current cell to advance
ffd4 _ _ l fwdfinddp  ; keep searching left


; > move datapointer back 1  (retreat / retract)
ret1 * * l ret2
ret2 _ _ l ret1
ret2 < < l retfinddp   ; locate the start of the tape


retfinddp _ _ l rfd1
rfd1 * * l rfd2
rfd2 * * l rfd3
rfd3 * * l rfd4

rfd4 > _ r retreattape  ; found current cell to retreat
rfd4 _ _ l retfinddp  ; keep searching left


retreattape * * r rt1
rt1 * * r rt2
rt2 * * r rt3
rt3 * * r x4   ; reuse the state from extend tape x4


; - subtract from current cell

dec1 * * l dec2
dec2 _ _ l dec1
dec2 < < l decfinddp   ; locate the start of the tape


decfinddp _ _ l dfd1
dfd1 * * l dfd2
dfd2 * * l dfd3
dfd3 * * l dfd4

dfd4 > > r dodec ; found current cell to decrement
dfd4 _ _ l decfinddp  ; keep searching left

dodec * * r dd1
dd1 * * r decc


; dec c pos
decc _ [ l decb  ; carry dec
decc > _ r r3
decc < > r r3
decc + < r r3
decc - + r r3
decc . - r r3
decc , . r r3
decc [ , l r3


; [ open bracket, do we enter or skip?

bra1 * * l bra2
bra2 _ _ l bra1
bra2 < < l brafinddp

brafinddp _ _ l bfd1
bfd1 * * l bfd2
bfd2 * * l bfd3
bfd3 * * l bfd4

bfd4 > > r testcell ; found current cell to test
bfd4 _ _ l brafinddp  ; keep searching left


testcell _ _ r t1  ;  a not set
t1 _ _ r t2    ; a b not set
; a set, do loop
t1 > > r r2
t1 < < r r2
t1 + + r r2
t1 - - r r2
t1 . . r r2
t1 , , r r2
t1 [ [ r r2


t2 _ _ r skiploop    ; a b c not set , don't enter loop


; b set, do loop
t2 > > r r3
t2 < < r r3
t2 + + r r3
t2 - - r r3
t2 . . r r3
t2 , , r r3
t2 [ [ r r3



; _ close bracket, do we loop back or continue?

end1 * * l end2
end2 _ _ l end1
end2 < < l endfinddp

endfinddp _ _ l efd1
efd1 * * l efd2
efd2 * * l efd3
efd3 * * l efd4

efd4 > > r endtestcell ; found current cell to test
efd4 _ _ l endfinddp  ; keep searching left

endtestcell _ _ r et1  ;  a not set
et1 _ _ r et2    ; a b not set
; a set, repeat loop
et1 > > r rl2
et1 < < r rl2
et1 + + r rl2
et1 - - r rl2
et1 . . r rl2
et1 , , r rl2
et1 [ [ r rl2

et2 _ _ r r1    ; a b c not set , don't repeat loop
; b set, repeat loop
et2 > > r rl3
et2 < < r rl3
et2 + + r rl3
et2 - - r rl3
et2 . . r rl3
et2 , , r rl3
et2 [ [ r rl3

; repeatloop is for when a ] was encountered, and we are not ready to exit the loop
; go back to IP, and search left for matching [ to repeat.

; this is a copy of return within the state of needing to repeat a loop
repeatloop * * r rl1
rl1 * * r rl2
rl2 * * r rl3
rl3 * * r rl4
rl4 < < r rlc0
rl4 _ _ r repeatloop


; running, move to current IP
rlc0 _ _ r rlcodefound
rlcodefound _ _ r rlc1
rlcodefound > _ l rlcf1
rlc1 * * r rlcodefound

; searching left for [] as part of our looking for a loop to repeat state
; rlsearchleft
; not interested in these values, keep looking
rlcf1 > > l rlcf2
rlcf1 < < l rlcf2
rlcf1 + + l rlcf2
rlcf1 - - l rlcf2
rlcf1 . . l rlcf2
rlcf1 , , l rlcf2

rlcf2 _ _ l rlcf1
; these are the loop symbols we care about:
rlcf1 [ [ l rlfoundstart
rlcf1 _ _ l rlfoundend

; rlfoundstart
; mark pos, then check whether nested counter is non-zero...
; if zero, we've found the start
; if non-zero, substract 1 and go back to looking
rlfoundstart * > l rlchecknested


