class Parser:
    def __init__(self):
        self._olines = []
        self._lab = 0
        self._labels = []
        self._flag = True  # je li parsiranje uspjesno?

    def parseFile(self, filename):
        # otvaramo datoteku s ekstenzijom ".vm"
        try:
            self._file = open(filename + ".vm", "r")
        except:
            Parser._error("file", -1, "cannot open source file")
            return

        self._name = filename  # ime datoteke
        self._ilines = []
        self._func = ""

        # citamo linije koda iz vm datoteke
        try:
            self._readFile()
        except:
            Parser._error("file", -1, "cannot read source file")
            return

        self._findLabels()

        # parsiramo vm kod liniju po liniju
        if not self._parseLines():
            return

    def writeFile(self, filename):
        # zapisujemo asemblerski kod
        try:
            self._file = open(filename + ".asm", "w")
        except:
            Parser._error("file", -1, "cannot open destination file")
            return

        try:
            self._writeFile()
        except:
            Parser._error("file", -1, "cannot write to destination file")
            return

    def _findLabels(self):
        for (line, n) in self._ilines:
            l = line.split("//")[0].split()
            if len(l) == 0:
                continue  # u slucaju prazne linije
            if l[0] == "label" and len(l) == 2:
                self._labels.append(l[1])

    def _parseLines(self):
        lines = []
        for (line, n) in self._ilines:
            l = self._parseLine(line, n)
            if not self._flag:
                return False
            if len(l) > 0:
                lines.append(l)
        self._olines = self._olines + lines
        return True

    def _parseLine(self, line, n):
        l = line.split("//")[0].split()
        if len(l) == 0 or len(l[0]) == 0:
            return ""

        if l[0] == "push":
            if len(l) == 3:
                if l[2].isdigit():
                    return "//" + " ".join(l) + "\n" + self._push(l[1], l[2], n)
                else:
                    self._flag = False
                    Parser._error("parser", n, "location must be a natural number")
                    return ""
            else:
                self._flag = False
                Parser._error("parser", n, "undefined command")
                return ""

        elif l[0] == "pop":
            if len(l) == 3:
                if l[2].isdigit():
                    return "//" + " ".join(l) + "\n" + self._pop(l[1], l[2], n)
                else:
                    self._flag = False
                    Parser._error("parser", n, "location must be a natural number")
                    return ""

        elif len(l) > 1 or l[0] == "return":
            if l[0] == "label" and len(l) == 2:
                return "//" + " ".join(l) + "\n" + self._label(l[1], n)
            elif l[0] == "goto" and len(l) == 2:
                if l[1] not in self._labels:
                    self._flag = False
                    Parser._error("goto", n, "invalid label")
                    return ""
                return "//" + " ".join(l) + "\n" + self._goto(l[1], n)
            elif l[0] == "if-goto" and len(l) == 2:
                if l[1] not in self._labels:
                    self._flag = False
                    Parser._error("ifgoto", n, "invalid label")
                    return ""
                return "//" + " ".join(l) + "\n" + self._ifgoto(l[1], n)
            elif l[0] == "function" and len(l) == 3:
                return "//" + " ".join(l) + "\n" + self._function(l[1], l[2], n)
            elif l[0] == "call" and len(l) == 3:
                return "//" + " ".join(l) + "\n" + self._call(l[1], l[2], n)
            elif l[0] == "return" and len(l) == 1:
                return "//" + " ".join(l) + "\n" + self._return(n)

        elif len(l) == 1:
            return "//" + " ".join(l) + "\n" + self._comm(l[0], n)

        return ""

    def _label(self, lab, n):
        return "(" + self._func + "$" + lab + ")"

    def _goto(self, lab, n):
        return "@" + self._func + "$" + lab + "\n0;JMP"

    def _ifgoto(self, lab, n):
        return "@SP\nAM=M-1\nD=M+1\n@" + self._func + "$" + lab + "\nD;JEQ"

    def _function(self, func, nvars, n):
        self._func = self._name + "." + func
        s = "(" + self._name + "." + func + ")"
        for i in range(int(nvars)):
            s += "\n@SP\nM=M+1\nA=M-1\nM=0"
        return s

    def _return(self, n):
        s = "@LCL\nD=M\n@R15\nM=D\n"
        s += "@5\nD=A\n@R15\nA=M-D\nD=M\n@R14\nM=D\n"
        s += "@SP\nAM=M-1\nD=M\n@ARG\nA=M\nM=D\n"
        s += "@ARG\nD=M+1\n@SP\nM=D\n"
        s += "@R15\nAM=M-1\nD=M\n@THAT\nM=D\n"
        s += "@R15\nAM=M-1\nD=M\n@THIS\nM=D\n"
        s += "@R15\nAM=M-1\nD=M\n@ARG\nM=D\n"
        s += "@R15\nAM=M-1\nD=M\n@LCL\nM=D\n"
        s += "@R14\nA=M\n0;JMP"
        return s

    def _call(self, func, nargs, n):
        retAddrLabel = func + "$ret" + str(self._lab)
        self._lab += 1
        s = "@" + retAddrLabel + "\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n"
        s += "@LCL\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n"
        s += "@ARG\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n"
        s += "@THIS\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n"
        s += "@THAT\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n"
        s += "@" + str(5 + int(nargs)) + "\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n"
        s += "@SP\nD=M\n@LCL\nM=D\n"
        s += "@" + func + "\n0;JMP\n"
        s += "(" + retAddrLabel + ")"
        return s

    def _push(self, src, ivx, n):
        if src == "constant":
            l = "@" + str(ivx) + "\nD=A\n"
        elif src == "local":
            l = "@" + str(ivx) + "\nD=A\n@LCL\nA=D+M\nD=M\n"
        elif src == "argument":
            l = "@" + str(ivx) + "\nD=A\n@ARG\nA=D+M\nD=M\n"
        elif src == "this":
            l = "@" + str(ivx) + "\nD=A\n@THIS\nA=D+M\nD=M\n"
        elif src == "that":
            l = "@" + str(ivx) + "\nD=A\n@THAT\nA=D+M\nD=M\n"
        elif src == "static":
            l = "@" + self._name + "." + str(ivx) + "\nD=M\n"
        elif src == "temp":
            l = "@" + str(5 + int(ivx)) + "\nD=M\n"
        elif src == "pointer":
            l = "@" + str(3 + int(ivx)) + "\nD=M\n"
        else:
            self._flag = False
            Parser._error("push", n, "undefined source \"" + src + "\"")
            return ""
        return l + "@SP\nM=M+1\nA=M-1\nM=D"

    def _pop(self, dst, ivx, n):
        if dst == "local":
            l = "@" + str(ivx) + "\nD=A\n@LCL\nD=D+M\n@R15\nM=D\n@SP\nAM=M-1\nD=M\n@R15\nA=M\nM=D"
        elif dst == "argument":
            l = "@" + str(ivx) + "\nD=A\n@ARG\nD=D+M\n@R15\nM=D\n@SP\nAM=M-1\nD=M\n@R15\nA=M\nM=D"
        elif dst == "this":
            l = "@" + str(ivx) + "\nD=A\n@THIS\nD=D+M\n@R15\nM=D\n@SP\nAM=M-1\nD=M\n@R15\nA=M\nM=D"
        elif dst == "that":
            l = "@" + str(ivx) + "\nD=A\n@THAT\nD=D+M\n@R15\nM=D\n@SP\nAM=M-1\nD=M\n@R15\nA=M\nM=D"
        elif dst == "static":
            l = "@SP\nAM=M-1\nD=M\n@" + self._name + "." + str(ivx) + "\nM=D"
        elif dst == "temp":
            l = "@SP\nAM=M-1\nD=M\n@" + str(5 + int(ivx)) + "\nM=D"
        elif dst == "pointer":
            l = "@SP\nAM=M-1\nD=M\n@" + str(3 + int(ivx)) + "\nM=D"
        else:
            self._flag = False
            Parser._error("push", n, "undefined destination \"" + dst + "\"")
            return ""
        return l

    def _comm(self, comm, n):
        if comm == "add":
            l = "@SP\nAM=M-1\nD=M\nA=A-1\nM=M+D"
        elif comm == "sub":
            l = "@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D"
        elif comm == "neg":
            l = "@SP\nA=M-1\nM=-M"
        elif comm == "and":
            l = "@SP\nAM=M-1\nD=M\nA=A-1\nM=M&D"
        elif comm == "or":
            l = "@SP\nAM=M-1\nD=M\nA=A-1\nM=M|D"
        elif comm == "not":
            l = "@SP\nA=M-1\nM=!M"
        elif comm == "eq":
            l = self._condJump("JEQ")
        elif comm == "gt":
            l = self._condJump("JGT")
        elif comm == "lt":
            l = self._condJump("JLT")
        else:
            self._flag = False
            Parser._error("command", n, "undefined command \"" + comm + "\"")
            return ""
        return l

    def _condJump(self, cond):
        l = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n@TRUE" + str(self._lab) + "\nD;" + cond + "\n@SP\nA=M-1\nM=0\n@CONT" + str(self._lab) + "\n0;JMP\n"
        l += "(TRUE" + str(self._lab) + ")\n@SP\nA=M-1\nM=-1\n"
        l += "(CONT" + str(self._lab) + ")"
        self._lab += 1
        return l

    @staticmethod
    def _error(source, line, message):
        print(source + " error on line " + str(line) + ": " + message)
