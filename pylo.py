#!./venv/bin/python
# pylo.py python logger
# keep notes alongside qsos
#

import cmd
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from colorama import init, Fore, Back, Style
from dateutil import parser
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
            self.start = parser.parse(content['start'])
            self.end = parser.parse(content['end'])
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
            '>',
            Fore.LIGHTRED_EX + (self.start.strftime('%a %d/%m ') + self.start.strftime('%H%M') + ('->' + self.end.strftime('%H%M') if self.end else '')),
            Fore.GREEN + (self.freq and str(self.freq) or 'f?'),
            Fore.RED + (self.mode or 'mo?'),
            Fore.LIGHTBLUE_EX + (self.act or 'do?'),
            Fore.RED + (self.callsign or 'dx?'),
            Fore.GREEN + (self.op or 'op?'),
            Fore.BLUE + ('s>' + (self.ops_rst or '?')),
            Fore.BLUE + ('r>' + (self.my_rst or '?')),
            Style.RESET_ALL + Style.DIM + f'[{self.id[0:7]}]',
            Style.RESET_ALL
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

    def update_from_dict(self, d):
        self.start = parser.parse(d['start'])
        try:
            self.end = parser.parse(d['end'])
        except:
            self.end = None
        self.mode = d['mode']
        try:
            self.freq = Decimal(d['freq'])
        except:
            self.freq = None
        self.act = d['act']
        self.callsign = d['callsign']
        self.op = d['op']
        self.my_rst = d['my_rst']
        self.ops_rst = d['ops_rst']
        self.notes = d['notes']
        self.id = d['id']


class PyloCmd(cmd.Cmd):
    intro = 'pylo 0.2'
    prompt = '% '
    
    def __init__(self, config):
        self.config = config

        # Open up db
        self.db = TinyDB(config['db_file'])
        self.log_table = self.db.table(config['log_table_name'])
        self.qso = QSO(self.config)
        try:
            last = self.log_table.all()[-1]
            self.qso.update_from_dict(last)
        except IndexError:
           pass

        super().__init__()

    def save_qso(self):
        self.log_table.upsert(self.qso.as_dict(), Query().id == self.qso.id)

    def do_new(self, args):
        freq = self.qso.freq
        mode = self.qso.mode
        act = self.qso.act
        self.save_qso()
        self.qso = QSO(self.config)
        self.qso.freq = freq
        self.qso.mode = mode
        self.qso.act = act

    def do_clr(self, args):
        self.qso = QSO(self.config)

    do_e = do_clr

    def do_save(self, args):
        self.save_qso()

    do_w = do_save

    def do_on(self, args):
        'Set start'
        self.qso.set_start_time(args)

    do_st = do_on

    def do_off(self, args):
        self.qso.set_end_time(args)

    do_x = do_off

    def do_freq(self, args):
        self.qso.freq = Decimal(args)

    do_f = do_freq
    do_fr = do_freq

    def do_mo(self, args):
        self.qso.mode = args.upper()

    do_m = do_mo

    def do_cw(self, args):
        self.qso.mode = 'CW'

    def do_ssb(self, args):
        self.qso.mode = 'SSB'

    def do_op(self, args):
        self.qso.op = args = args.title()

    do_name = do_op
    do_n = do_op

    def do_dx(self, args):
        self.qso.callsign = args.upper()

    do_call = do_dx

    def do_rr(self, args):
        if args:
            self.qso.callsign = args.upper()
        self.qso.act = 'QSO'

    def do_cq(self, args):
        self.qso.act = 'CQ'

    def do_do(self, args):
        self.qso.act = args.upper()

    def do_qso(self, args):
        self.qso.act = 'QSO'

    def do_heard(self, args):
        self.qso.act = 'HEARD'
        if args:
            self.do_dx(args)

    do_h = do_heard

    def do_rs(self, args):
        self.qso.ops_rst = args

    do_s = do_rs

    def do_my(self, args):
        self.qso.my_rst = args

    do_r = do_my

    def do_list(self, args):
        for l in self.qso.notes:
            print(l)

    do_l = do_list

    def do_undo(self, args):
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