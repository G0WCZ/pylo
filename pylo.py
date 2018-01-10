#!./venv/bin/python
# pylo.py python logger
# keep notes alongside qsos
#

import cmd
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import dateutil
from tinydb import TinyDB, Query


class Log():
    """
    Represents a log instance
    """
    pass

class QSO():
    """
    Basic components of a QSO/Log entry
    """
    def __init__(self, config, content=None):
        super().__init__()
        self.me = config['my_call']
        if content:
            self.start = dateutil.parser(content['start'])
            self.end = dateutil.parser(content['end'])
            self.mode = content['mode']
            self.freq = Decimal(content['freq'])
            self.act = content['act']
            self.callsign = content['callsign']
            self.op = content['op']
            self.my_rst = content['my_rst']
            self.ops_rst = content['ops_rst']
            self.notes = content['notes']
            self.id = content['id']
        else:
            self.callsign = None
            self.op = None
            self.start = datetime.utcnow()
            self.end = None
            self.mode = None # cw, ssb etc
            self.freq = None
            self.act = None   # qso or cq or tx or rx
            self.ops_rst = None
            self.my_rst = None
            self.notes = []
            self.id = uuid4().hex

    def set_start_time(self, args):
        self.start = datetime.utcnow()

    def set_end_time(self, args):
        self.end = datetime.utcnow()

    def line(self, comment='?'):
        line = [
            f'<{comment}>',
            self.start.strftime('%H%M') + ('->' + self.end.strftime('%H%M') if self.end else ''),
            self.freq and str(self.freq) or 'f?',
            self.mode or 'mo?',
            self.act or 'do?',
            self.callsign or 'dx?',
            self.op or 'op?',
            's>' + (self.ops_rst or '?'),
            'r>' + (self.my_rst or '?'),
            f'[{self.id[0:7]}]'
        ]
        return ' '.join(line)

    def as_dict(self):
        return {
            'start': self.start.isoformat(),
            'end': self.end and self.end.isoformat(),
            'mode': self.mode,
            'freq': self.freq and str(self.freq),
            'act': self.act,
            'callsign': self.callsign,
            'op': self.op,
            'my_rst': self.my_rst,
            'ops_rst': self.ops_rst,
            'notes': self.notes,
            'id': self.id
        }


class PyloCmd(cmd.Cmd):
    intro = 'pylo 0.2'
    prompt = '% '
    
    def __init__(self, config):
        self.config = config
        self.qso = QSO(self.config)

        # Open up db
        self.db = TinyDB(config['db_file'])
        self.log_table = self.db.table(config['log_table_name'])

        super().__init__()

    def save_qso(self):
        self.log_table.upsert(self.qso.as_dict(), Query().id == self.qso.id)

    def do_new(self, args):
        self.save_qso()
        self.qso = QSO(self.config)

    def do_save(self, args):
        self.save_qso()

    def do_st(self, args):
        'Set start'
        self.qso.set_start_time(args)

    def do_sk(self, args):
        self.qso.set_end_time(args)

    def do_fr(self, args):
        self.qso.freq = Decimal(args)

    do_f = do_fr

    def do_mo(self, args):
        self.qso.mode = args.upper()

    do_m = do_mo

    def do_op(self, args):
        self.qso.op = args = args.title()

    def do_dx(self, args):
        self.qso.callsign = args.upper()

    do_h = do_dx

    def do_time(self, args):
        pass

    def do_rr(self, args):
        if args:
            self.qso.callsign = args.upper()
        self.qso.act = 'qso'

    def do_cq(self, args):
        self.qso.act = 'cq'

    def do_do(self, args):
        self.qso.act = args.upper()

    def do_rs(self, args):
        self.qso.ops_rst = args

    do_ur = do_rs

    def do_my(self, args):
        self.qso.my_rst = args

    def do_no(self, args):
        for l in self.qso.notes:
            print(l)

    do_n = do_no

    def do_un(self, args):
        self.qso.notes.pop()

    def default(self, line):
        if line[0] == '.':
            self.qso.notes.append(line[2:])


    def do_EOF(self, args):
        self.save_qso()
        print('73 sk')
        exit(0)

    def postcmd(self, stop, line):
        print(self.qso.line('r'))
        return False

config = {
    'my_call': 'G0WCZ',
    'db_file': './logs/G0WCZ1.json',
    'log_table_name': 'main'
}

if __name__ == '__main__':
    PyloCmd(config).cmdloop()