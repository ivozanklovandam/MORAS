import re

def _parse_macros(self):
    self._while_iter = 0
    self._while_open = []
    self._iter_lines(self._parse_macro)
    if len(self._while_open):
      self._flag = False
      self._errm = "While not closed."

def _parse_macro(self, line, p, o):
    if line[0] != "$":
        return line
    else:
        lines = []
        if re.search("^\$MV\((\d|\w)+,(\d|\w)+\)$", line) != None:
          A = re.split("[(,)]", line)[1]
          B = re.split("[(,)]", line)[2]
          lines.append("@" + A)
          lines.append("D=M")
          lines.append("@" + B)
          lines.append("M=D")
        elif re.search("^\$SWP\((\d|\w)+,(\d|\w)+\)$", line) != None:
          A = re.split("[(,)]", line)[1]
          B = re.split("[(,)]", line)[2]
          lines.append("@" + A)
          lines.append("D=M")
          lines.append("@SWP")
          lines.append("M=D")
          lines.append("@" + B)
          lines.append("D=M")
          lines.append("@" + A)
          lines.append("M=D")
          lines.append("@SWP")
          lines.append("D=M")
          lines.append("@" + B)
          lines.append("M=D")
        elif re.search("^\$SUM\((\d|\w)+,(\d|\w)+,(\d|\w)+\)$", line) != None:
          A = re.split("[(,)]", line)[1]
          B = re.split("[(,)]", line)[2]
          D = re.split("[(,)]", line)[3]
          lines.append("@" + A)
          lines.append("D=M")
          lines.append("@" + B)
          lines.append("D=D+M")
          lines.append("@" + D)
          lines.append("M=D")
        elif re.search("^\$WHILE\((\d|\w)+\)$", line) != None:
          n = re.split("[()]", line)[1]
          self._while_open.append(self._while_iter)
          lines.append("(WHILE" + str(self._while_iter) + ")")
          lines.append("@" + n)
          lines.append("D=M")
          lines.append("@WHILE_END" + str(self._while_iter))
          lines.append("D;JEQ")
          self._while_iter += 1
        elif re.search("^\$END$", line) != None:
          if len(self._while_open) == 0:
            self._flag = False
            self._line = o
            self._errm = "Ending a non existing loop."
          else:
            n = self._while_open.pop()
            lines.append("@WHILE" + str(n))
            lines.append("0;JMP")
            lines.append("(WHILE_END" + str(n) + ")")
        else:
            self._flag = False
            self._line = o
            self._errm = "Invalid macro"
        return lines
