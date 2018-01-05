# pylo.py python logger
# keep notes alongside qsos
#

import cmd
from datetime import datetime
from decimal import Decimal

class Field():
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

    def validate(self, args):
        return True

    def store(self, args):
        pass

    def print(self):
        print(self.value)

    def set(self, value):
        self.value = value

class Log():
    """
    Represents a log instance
    """
    pass

class QSO(dict):
    """
    Basic components of a QSO/Log entry
    """
    def __init__(self):
        super().__init__()
        self.me = 'G0WCZ'
        self.callsign = None
        self.op = None
        self.start = datetime.utcnow()
        self.end = None
        self.mode = 'cw' # cw, ssb etc
        self.freq = Decimal('0.000')
        self.act = None   # qso or cq or tx or rx
        self.ops_rst = None
        self.my_rst = None
        self.notes = []

    def set_start_time(self, args):
        self.start = datetime.utcnow()

    def set_end_time(self, args):
        self.end = datetime.utcnow()

    def line(self, comment='?'):
        line = [
            f'<{comment}>',
            self.start.strftime('%H%M') + ('->' + self.end.strftime('%H%M') if self.end else ''),
            str(self.freq) or 'f?',
            self.mode or 'mo?',
            self.act or 'do?',
            self.callsign or 'dx?',
            self.op or 'op?',
            's>' + (self.ops_rst or '?'),
            'r>' + (self.my_rst or '?'),
        ]
        return ':'.join(line)

class LogSh(cmd.Cmd):
    intro = 'LogSh v0.1'
    prompt = '% '
    
    def __init__(self):
        self.qso = QSO();
        super().__init__()

    def do_new(self, args):
        self.qso = QSO()

    def do_st(self, args):
        'Set start'
        self.qso.set_start_time(args)

    def do_sk(self, args):
        self.qso.set_end_time(args)

    def do_fr(self, args):
        self.qso.freq = Decimal(args)

    do_f = do_fr

    def do_mo(self, args):
        self.qso.mode = args

    def do_op(self, args):
        self.qso.op = args

    def do_dx(self, args):
        self.qso.callsign = args

    do_h = do_dx

    def do_time(self, args):
        pass

    def do_rr(self, args):
        if args:
            self.qso.callsign = args
        self.qso.act = 'qso'

    def do_cq(self, args):
        self.qso.act = 'cq'

    def do_rs(self, args):
        self.qso.ops_rst = args

    def do_my(self, args):
        self.qso.my_rst = args

    def do_no(self, args):
        for l in self.qso.notes:
            print(l)

    def do_un(self, args):
        self.qso.notes.pop()

    def default(self, line):
        if line[0] == '.':
            self.qso.notes.append(line)

    def do_EOF(self, args):
        print('73 sk')
        exit(0)

    def postcmd(self, stop, line):
        print(self.qso.line('r'))
        return False

if __name__ == '__main__':
    LogSh().cmdloop()