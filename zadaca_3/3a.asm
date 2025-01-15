@R2
M=1

@R1
D=M
@i
M=D

$WHILE(i)
@R0
D=M
@j
M=D
@R3
M=0
$WHILE(j)
$SUM(R3,R2,R3)
@j
M=M-1
$END
$MV(R3, R2)
@i
M=M-1
$END

(End)
@End
0;JMP
