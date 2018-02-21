from decimal import Decimal
import unittest


from pylo import QSO


class TestQSO(unittest.TestCase):

    def test_construct(self):
        qso = QSO({'my_call': 'AAA'})
        self.assertTrue(isinstance(qso, QSO))

    def test_mycall(self):
        qso = QSO({'my_call': 'G0WCZ'})
        self.assertEqual(qso.me, 'G0WCZ')

    def test_no_content(self):
        qso = QSO({'my_call': 'G0WCZ'})
        self.assertIsNone(qso.callsign)
        self.assertIsNone(qso.op)
        self.assertIsNone(qso.end)
        self.assertIsNone(qso.mode)
        self.assertIsNone(qso.freq)
        self.assertIsNone(qso.act)
        self.assertIsNone(qso.ops_rst)
        self.assertIsNone(qso.my_rst)
        self.assertEqual(qso.notes, [])
        self.assertEqual(len(qso.id), 32)

    def test_content(self):
        content = {
            'start': '2018-04-01',
            'end': '2018-04-02',
            'mode': 'SSB',
            'freq': '14.200',
            'act': 'L',
            'callsign': 'AA1AA',
            'op': 'Joe',
            'my_rst': '339',
            'ops_rst': '559',
            'notes': ['a', 'b', 'c'],
            'id': 'an-id'
        }
        qso = QSO({'my_call': 'G0WCZ'}, content)
        self.assertEqual(qso.start.year, 2018)
        self.assertEqual(qso.end.day, 2)
        self.assertEqual(qso.mode, 'SSB')
        self.assertEqual(qso.freq, Decimal('14.200'))
        self.assertEqual(qso.act, 'L')
        self.assertEqual(qso.callsign, 'AA1AA')
        self.assertEqual(qso.op, 'Joe')
        self.assertEqual(qso.my_rst, '339')
        self.assertEqual(qso.ops_rst, '559')
        self.assertEqual(qso.notes, ['a', 'b', 'c'])
        self.assertEqual(qso.id, 'an-id')

