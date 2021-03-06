# coding: utf8
from ztest.test_case import BaseCase
from jsondb.pattern import Pattern
from jsondb.project import Project
from jsondb.document import Field, Document


class Test(BaseCase):

    def setUp(self):
        self.project = Project()
        self.table = self.project.add('test')
        self.pattern = self.table.pattern

    def test_add_int_pattern(self):
        doc = self.table.add(1)
        self.eq(doc.pattern.type, Pattern.DICT)

        pattern_field_int = self.pattern.add('field_int', type=Pattern.INT, default=12)
        self.isinstance(doc.get('field_int'), Field)
        self.eq(doc.get('field_int').pattern.type, Pattern.INT)
        self.eq(doc.get('field_int').pattern, pattern_field_int)
        self.eq(doc.get('field_int').get(), pattern_field_int.default)

    def test_add_list_pattern(self):
        doc = self.table.add(1)

        pattern_list = self.pattern.add('field_list', type=Pattern.LIST)
        self.isinstance(doc.get('field_list'), Document)
        self.eq(doc.get('field_list').pattern.type, Pattern.LIST)
        self.eq(doc.get('field_list').pattern, pattern_list)
        self.eq(doc.get('field_list').type_list, 'list')

    def create_pattern(self):
        self.pattern.add('text', type=Pattern.DICT)
        self.pattern.get('text').add('ru', type=Pattern.DICT)
        self.pattern.get('text').get('ru').add('title', type=Pattern.STR,
                                               default='русский заголовок')
        self.pattern.get('text').add('eng', type=Pattern.DICT)
        self.pattern.get('text').get('eng').add('title', type=Pattern.STR,
                                                default='english title')

        self.pattern.add('gift', type=Pattern.LIST)
        self.pattern.get('gift').items.add('type', type=Pattern.STR,
                               values=['coins', 'coins_gold'], default='coins')
        self.pattern.get('gift').items.add('value', type=Pattern.LIST,
                                           item_type=Pattern.INT)
        self.pattern.get('gift').items.get('value').items.default = 12

    def test_pattern(self):
        self.create_pattern()

        data = {'text': {'ru': {'title': 'test value'},
                         'eng': {'title': 'sample'}},
                'gift': [{'type':'coins1', 'value':[1]},
                         {'type':'coins_gold', 'value':[1, 34]}]
                }
        doc = self.table.add(1, data=data)

        self.eq(doc.data(), {'text': {'ru': {'title': 'test value'},
          'eng': {'title': 'sample'}}, 'gift': [{'type':'coins', 'value':[1]},
                                    {'type':'coins_gold', 'value':[1, 34]}]})
        self.eq(doc.get('text').get('ru').get('title').get(), 'test value')
        self.eq(doc.get('text').get('eng').get('title').get(), 'sample')

        #
        gift = doc.get('gift').add(data=\
                                {'type': 'coins_gold', 'value': [5, 4, 67, '']})
        self.eq(gift.data(), {'type': 'coins_gold', 'value': [5, 4, 67, 12]})
        self.eq(doc.get('gift').length(), 3)

        #
        new_doc = self.table.add(2, data=doc.data())
        self.eq(new_doc.data(), doc.data())

    def test_signals(self):
        self.create_pattern()

        doc = self.table.add(1)

        # add signal
        self.pattern.add('price', type=Pattern.DICT)
        self.pattern.get('price').add('type', type=Pattern.STR, default='type')
        self.pattern.get('price').add('value', type=Pattern.INT, default=100)
        self.eq(doc.get('price').data(), {'type': 'type', 'value': 100})

        self.pattern.add('list', type=Pattern.LIST, item_type=Pattern.LIST)
        self.pattern.get('list').items.items.add('param', type=Pattern.STR, default='test')
        self.pattern.get('list').items.items.add('include_list', type=Pattern.LIST)
        self.eq(doc.get('list').type_list, 'list')
        self.eq(doc.get('list').pattern.type, Pattern.LIST)
        self.eq(doc.get('list').pattern.items.type, Pattern.LIST)
        self.eq(doc.get('list').pattern.items.items.type, Pattern.DICT)
        self.eq(doc.get('list').pattern.items.items.get('param').type, Pattern.STR)
        self.eq(doc.get('list').pattern.items.items.get('include_list').type, Pattern.LIST)
        self.eq(doc.get('list').pattern.items.items.get('include_list').items.type, Pattern.DICT)

        doc.get('list').add()
        self.eq(doc.get('list').get(0).type_list, 'list')
        self.eq(doc.get('list').data(), [[]])

        doc.get('list').get(0).add()
        doc.get('list').get(0).get(0).get('include_list').add()
        self.eq(doc.get('list').data(), [[{'param':'test', 'include_list':[{}]}]])

        # remove and change_type_item signal
        self.pattern.get('list').items.items.remove('include_list')
        self.eq(doc.get('list').data(), [[{'param':'test'}]])

        self.pattern.get('list').items.items.remove('param')
        self.eq(doc.get('list').data(), [[{}]])

        self.pattern.get('list').items.change_type_item(Pattern.INT, default=45)
        self.eq(doc.get('list').data(), [[]])
        doc.get('list').get(0).add()
        self.eq(doc.get('list').data(), [[45]])

        self.pattern.get('list').change_type_item(Pattern.DICT)
        self.eq(doc.get('list').data(), [])
        doc.get('list').add()
        self.eq(doc.get('list').data(), [{}])
