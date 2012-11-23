# coding: utf8
from ztest.test_case import BaseCase
from jsondb.project import Project
from jsondb.pattern import Pattern, PatternError
from jsondb.document import Document


class Test(BaseCase):

    def setUp(self):
        self.project = Project()
        self.table = self.project.add('test')

    def test_int(self):
        pattern_int = self.table.pattern.add('field_int', type=Pattern.INT, \
                                             default=1, min= -5, max=10)

        self.eq(pattern_int.type, Pattern.INT)
        self.eq(pattern_int.default, 1)
        self.eq(pattern_int.max, 10)
        self.eq(pattern_int.min, -5)

        doc = self.table.add(1)
        self.eq(doc.get('field_int').get(), 1)

        doc.get('field_int').set(3)
        self.eq(doc.get('field_int').get(), 3)

        doc.get('field_int').set(-6)
        self.eq(doc.get('field_int').get(), 3)

        doc.get('field_int').set(11)
        self.eq(doc.get('field_int').get(), 3)

        doc.get('field_int').set(-5)
        self.eq(doc.get('field_int').get(), -5)

        doc.get('field_int').set(10)
        self.eq(doc.get('field_int').get(), 10)

        # not min
        pattern_int.min = None
        doc.get('field_int').set(-100)
        self.eq(doc.get('field_int').get(), -100)

        # not max
        pattern_int.max = None
        doc.get('field_int').set(100)
        self.eq(doc.get('field_int').get(), 100)

        # add values in pattern
        doc.get('field_int').set(1)
        pattern_int.values = [1, 2, 6]

        doc.get('field_int').set(2)
        self.eq(doc.get('field_int').get(), 2)

        doc.get('field_int').set(6)
        self.eq(doc.get('field_int').get(), 6)

        doc.get('field_int').set(2)
        self.eq(doc.get('field_int').get(), 2)

        doc.get('field_int').set(0)
        self.eq(doc.get('field_int').get(), 2)

    def test_float(self):
        pattern_int = self.table.pattern.add('field', type=Pattern.FLOAT, \
                                             default=1.2, min= -5.1, max=10.6)

        self.eq(pattern_int.type, Pattern.FLOAT)
        self.eq(pattern_int.default, 1.2)
        self.eq(pattern_int.max, 10.6)
        self.eq(pattern_int.min, -5.1)

        doc = self.table.add(1)
        self.eq(doc.get('field').get(), 1.2)

        doc.get('field').set(3.6)
        self.eq(doc.get('field').get(), 3.6)

        doc.get('field').set(-5.11)
        self.eq(doc.get('field').get(), 3.6)

        doc.get('field').set(10.7)
        self.eq(doc.get('field').get(), 3.6)

        doc.get('field').set(-5.05)
        self.eq(doc.get('field').get(), -5.05)

        doc.get('field').set(10.4)
        self.eq(doc.get('field').get(), 10.4)

        # not min
        pattern_int.min = None
        doc.get('field').set(-100.156)
        self.eq(doc.get('field').get(), -100.156)

        # not max
        pattern_int.max = None
        doc.get('field').set(100.89)
        self.eq(doc.get('field').get(), 100.89)

        # add values in pattern
        doc.get('field').set(1.2)
        pattern_int.values = [1.2, 2.36, 6.598]

        doc.get('field').set(2.36)
        self.eq(doc.get('field').get(), 2.36)

        doc.get('field').set(6.598)
        self.eq(doc.get('field').get(), 6.598)

        doc.get('field').set(2.36)
        self.eq(doc.get('field').get(), 2.36)

        doc.get('field').set(0.358)
        self.eq(doc.get('field').get(), 2.36)

    def test_str(self):
        pattern = self.table.pattern.add('field', type=Pattern.STR, \
                                             default='t')

        self.eq(pattern.type, Pattern.STR)
        self.eq(pattern.default, 't')

        doc = self.table.add(1)
        self.eq(doc.get('field').get(), 't')

        pattern.values = ['a', 'b', 'c']
        doc.get('field').set('a')
        self.eq(doc.get('field').get(), 'a')

        doc.get('field').set('c')
        self.eq(doc.get('field').get(), 'c')

        doc.get('field').set('x')
        self.eq(doc.get('field').get(), 'c')

    def test_signal(self):
        first = self.table.add(1)

        pattern = self.table.pattern.add('field', type=Pattern.INT, \
                                         default=12)

        second = self.table.add(2)
        self.eq(second.get('field').get(), 12)

        self.eq(first.get('field').get(), 12)

        self.eq(pattern, first.get('field').pattern)
        self.eq(first.get('field').pattern, second.get('field').pattern)

        # dict
        pattern = self.table.pattern.add('field_dict', type=Pattern.DICT)
        self.isinstance(first.get('field_dict'), Document)
        self.isinstance(second.get('field_dict'), Document)

    def test_pattern_items(self):
        pattern = self.table.pattern.add('list', type=Pattern.LIST)
        self.eq(pattern.type, Pattern.LIST)

        self.assertRaises(PatternError, pattern.add, ('test',))
        self.assertRaises(PatternError, pattern.get, ('test',))
        self.assertRaises(PatternError, pattern.remove, ('test',))
        self.assertRaises(PatternError, pattern.remove_all)

        self.isinstance(pattern.items, Pattern)
        self.eq(pattern.items.type, Pattern.DICT)

    def test_add_pattern_int(self):
        pattern = self.table.pattern.add('pattern', type=Pattern.INT)

        self.eq(pattern.type, Pattern.INT)

        self.assertRaises(PatternError, pattern.add, ('test',))
        self.assertRaises(PatternError, pattern.get, ('test',))
        self.assertRaises(PatternError, pattern.remove, ('test',))
        self.assertRaises(PatternError, pattern.remove_all)

    def test_add_pattern_float(self):
        pattern = self.table.pattern.add('pattern', type=Pattern.FLOAT)

        self.eq(pattern.type, Pattern.FLOAT)

        self.assertRaises(PatternError, pattern.add, ('test',))
        self.assertRaises(PatternError, pattern.get, ('test',))
        self.assertRaises(PatternError, pattern.remove, ('test',))
        self.assertRaises(PatternError, pattern.remove_all)

    def test_add_pattern_str(self):
        pattern = self.table.pattern.add('pattern', type=Pattern.STR)

        self.eq(pattern.type, Pattern.STR)

        self.assertRaises(PatternError, pattern.add, ('test',))
        self.assertRaises(PatternError, pattern.get, ('test',))
        self.assertRaises(PatternError, pattern.remove, ('test',))
        self.assertRaises(PatternError, pattern.remove_all)
