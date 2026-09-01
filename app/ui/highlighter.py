from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor,QFont,QSyntaxHighlighter,QTextCharFormat
class ShellHighlighter(QSyntaxHighlighter):
    def __init__(self,doc):
        super().__init__(doc); self.rules=[]
        for p,c,b in [(r"\b(config|show|redis-cli|sonic-cfggen|systemctl|grep|awk|jq|echo|cp|sha256sum)\b","#4ea1ff",1),(r"\b(reload|factory-reset|reboot|rm)\b","#ff5c5c",1),(r"#[^\n]*","#6a9955",0),(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b","#d19a66",0)]:
            f=QTextCharFormat(); f.setForeground(QColor(c));
            if b: f.setFontWeight(QFont.Weight.Bold)
            self.rules.append((QRegularExpression(p),f))
    def highlightBlock(self,text):
        for rx,fmt in self.rules:
            it=rx.globalMatch(text)
            while it.hasNext(): m=it.next(); self.setFormat(m.capturedStart(),m.capturedLength(),fmt)
