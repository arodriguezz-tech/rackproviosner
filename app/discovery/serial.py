from PySide6.QtCore import QObject,Signal,QTimer,QIODevice
from PySide6.QtSerialPort import QSerialPort,QSerialPortInfo
class SerialSession(QObject):
    console=Signal(str); event=Signal(str,object)
    def __init__(self):
        super().__init__(); self.port=QSerialPort(self); self.pending=None; self.buffer=""; self.timer=QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self._done); self.port.readyRead.connect(self._read); self.port.errorOccurred.connect(self._error)
    @staticmethod
    def available_ports(): return [p.portName() for p in QSerialPortInfo.availablePorts()]
    def open(self,name,baud):
        self.port.setPortName(name); self.port.setBaudRate(int(baud)); self.port.setDataBits(QSerialPort.DataBits.Data8); self.port.setParity(QSerialPort.Parity.NoParity); self.port.setStopBits(QSerialPort.StopBits.OneStop); self.port.setFlowControl(QSerialPort.FlowControl.NoFlowControl); ok=self.port.open(QIODevice.OpenModeFlag.ReadWrite); self.event.emit("serial.connected",{"ok":ok,"port":name,"baud":baud}); return ok
    def close(self): self.port.close(); self.event.emit("serial.disconnected",{})
    def run(self,name,command,wait=2500):
        if not self.port.isOpen(): self.event.emit("serial.blocked",{"reason":"Port is not connected"}); return
        if self.pending: self.event.emit("serial.blocked",{"reason":"Command already running"}); return
        self.pending=name; self.buffer=""; self.event.emit("serial.command.started",{"name":name,"command":command}); self.port.write((command+"\n").encode()); self.timer.start(wait)
    def _read(self):
        s=bytes(self.port.readAll()).decode("utf-8",errors="replace"); self.buffer+=s; self.console.emit(s)
    def _done(self):
        if self.pending: n=self.pending; self.pending=None; self.event.emit("serial.command.finished",{"name":n,"output":self.buffer})
    def _error(self,e):
        if e!=QSerialPort.SerialPortError.NoError: self.event.emit("serial.error",{"message":self.port.errorString()})
