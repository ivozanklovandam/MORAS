@R0
D=M
@n
M=D

$WHILE(n) // 7 -> 1
@R0
D=M
@i
M=D-1
$WHILE(i) // 6 -> 1
@100
D=A
@i
D=D+M   // 106 -> 101
A=D
D=M    // RAM[106] -> RAM[101]
A=A-1
D=D-M  // RAM[106] - RAM[105] -> RAM[101] - RAM[100]
@SWAP
D;JLE
(back)
@i
M=M-1
$END
@n
M=M-1
$END

(End)
@End
0;JMP

(SWAP)
@100
D=A
@i
D=D+M
A=D   // oso na veci
D=M
@tmp  // strpo ga u tmp
M=D
@100  
D=A
@i
D=D+M
A=D
A=A-1   // oso na manji
D=M    // strpo manji u D
A=A+1   // oso u veci
M=D    // strpo D u veci 

@100  
D=A
@i
D=D+M
D=D-1  // oso na manji
@tmp2 //spremio adresu u ovo smece
M=D
@tmp
D=M
@tmp2
A=M
M=D

@back
0;JMP
