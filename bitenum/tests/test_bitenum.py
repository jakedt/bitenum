import unittest

from bitenum import BitEnum


class _SequentialFlag(BitEnum):
    one = 1
    two = 2
    four = 4
    eight = 8


class _GapFlag(BitEnum):
    two = 2
    eight = 8
    thirtytwo = 32


class TestBitEnum(unittest.TestCase):
    def test_equality(self):
        self.assertEqual(_SequentialFlag.one, _SequentialFlag.one)
        self.assertEqual(_SequentialFlag(1), _SequentialFlag.one)
        self.assertEqual(_GapFlag(2), _GapFlag.two)

        self.assertNotEqual(_SequentialFlag.two, _SequentialFlag.one)
        self.assertNotEqual(_SequentialFlag.two, _GapFlag.two)
        self.assertNotEqual(1, _SequentialFlag.one)

    def test_set_operators(self):
        # Union
        self.assertEqual(_SequentialFlag(5),
                         _SequentialFlag.one | _SequentialFlag.four)
        self.assertEqual(_GapFlag(34), _GapFlag.two | _GapFlag.thirtytwo)
        self.assertTrue(isinstance(_GapFlag.two | _GapFlag.thirtytwo,
                                   _GapFlag))

        # Intersection
        self.assertEqual(_SequentialFlag(1),
                         _SequentialFlag(5) & _SequentialFlag.one)

        # Compound
        self.assertEqual(_GapFlag(34), ((_GapFlag.two |
                                         _GapFlag.eight |
                                         _GapFlag.thirtytwo) &
                                        (_GapFlag.two |
                                         _GapFlag.thirtytwo)))

        # Negation
        self.assertEqual(_GapFlag(34), ~_GapFlag.eight)
        self.assertEqual(_SequentialFlag(10),
                         ~(_SequentialFlag.one | _SequentialFlag.four))

    def test_iteration(self):
        all_sequential = list(_SequentialFlag(15))
        self.assertEqual([_SequentialFlag.one,
                          _SequentialFlag.two,
                          _SequentialFlag.four,
                          _SequentialFlag.eight],
                         all_sequential)

        some_gap = list(_GapFlag(34))
        self.assertEqual([_GapFlag.two, _GapFlag.thirtytwo], some_gap)

        # Iteration order
        ooo_definition = (_SequentialFlag.one |
                          _SequentialFlag.four |
                          _SequentialFlag.two)
        in_order = list(ooo_definition)
        self.assertEqual([_SequentialFlag.one,
                          _SequentialFlag.two,
                          _SequentialFlag.four],
                         in_order)

        # Instance equality
        self.assertTrue(_SequentialFlag.one is _SequentialFlag(1))
        self.assertTrue(_GapFlag.two is _GapFlag(2))
        self.assertFalse(_GapFlag.two is _SequentialFlag.two)

        iterated_one = list(_SequentialFlag.two | _SequentialFlag.one)[0]
        self.assertTrue(iterated_one is _SequentialFlag.one)

    def test_comparison(self):
        self.assertTrue(_SequentialFlag.one < _SequentialFlag.two)
        self.assertTrue(_SequentialFlag.two > _SequentialFlag.one)
        self.assertTrue(_SequentialFlag.two == _SequentialFlag.two)

        with self.assertRaises(TypeError):
            self.assertFalse(_GapFlag.two < _SequentialFlag.two)

        with self.assertRaises(TypeError):
            self.assertFalse(_GapFlag.two > _SequentialFlag.two)

        # Can't sort a list of heterogeneous types
        with self.assertRaises(TypeError):
            list(sorted([_SequentialFlag.one, _GapFlag.two]))

        with self.assertRaises(TypeError):
            list(sorted([_SequentialFlag.one, 2]))

        with self.assertRaises(TypeError):
            list(sorted([2, _SequentialFlag.one]))

        self.assertFalse(_GapFlag.two == _SequentialFlag.two)

        self.assertTrue((_SequentialFlag.one | _SequentialFlag.two) >
                        _SequentialFlag(2))
        self.assertTrue((_SequentialFlag.one | _SequentialFlag.two) <
                        _SequentialFlag.four)

        self.assertEqual([_GapFlag.two, _GapFlag.eight, _GapFlag.thirtytwo],
                         list(sorted([_GapFlag.eight, _GapFlag.thirtytwo,
                                      _GapFlag.two])))

    def test_bad_constructors(self):
        with self.assertRaises(ValueError):
            _SequentialFlag(16)

        with self.assertRaises(ValueError):
            _GapFlag(9)

        with self.assertRaises(ValueError):
            _SequentialFlag(-1)

        with self.assertRaises(TypeError):
            _SequentialFlag("2")

        # Testing that this doesn't raise an exception
        self.assertEqual(_SequentialFlag(0), _SequentialFlag(0))

    def test_disabled(self):
        with self.assertRaises(NotImplementedError):
            _SequentialFlag.one += _SequentialFlag.four

    def test_repr(self):
        self.assertEqual('_GapFlag(2)', repr(_GapFlag.two))
        self.assertEqual('_GapFlag(10)', repr(_GapFlag.two | _GapFlag.eight))

    def test_bad_classes(self):
        with self.assertRaises(ValueError):
            type('DuplicateField', (BitEnum,), dict(one=1, two=1))

        with self.assertRaises(ValueError):
            type('NotPowerTwo', (BitEnum,), dict(one=1, two=3))

        with self.assertRaises(TypeError):
            type('StringField', (BitEnum,), dict(one=1, two="2"))

    def test_invalid_setattr(self):
        Basic = type('Basic', (BitEnum,), dict(one=1))

        with self.assertRaises(AttributeError):
            Basic.fail = lambda x: 1

        with self.assertRaises(AttributeError):
            Basic.one.fail = lambda x: 1

        with self.assertRaises(AttributeError):
            Basic.one = Basic(1)
