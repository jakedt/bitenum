import math

from collections import OrderedDict
from threading import Lock
from six import add_metaclass


class _BitEnumMeta(type):
    __unfrozen = Lock()

    INT_TO_WRAP = {
        '__or__',
        '__ror__',
        '__and__',
        '__rand__',
        '__xor__',
        '__rxor__',
        '__lshift__',
        '__rshift__',
        '__rlshift__',
        '__rrshift__',
        '__mod__',
        '__rmod__',
        '__div__',
        '__rdiv__',
        '__floordiv__',
        '__rfloordiv__',
        '__divmod__',
        '__rdivmod__',
        '__mul__',
        '__rmul__',
        '__sub__',
        '__rsub__',
        '__add__',
        '__radd__',
        '__pow__',
        '__rpow__',
    }

    PY3_REMOVED = {
        '__rdiv__',
        '__idiv__',
        '__div__',
    }

    INT_TO_DISABLE = {
        '__iadd__',
        '__isub__',
        '__imul__',
        '__ifloordiv__',
        '__idiv__',
        '__itruediv__',
        '__imod__',
        '__ipow__',
        '__ilshift__',
        '__irshift__',
        '__iand__',
        '__ior__',
        '__ixor__',
    }

    def __setattr__(cls, name, value):
        if cls.__unfrozen.locked():
            super(_BitEnumMeta, cls).__setattr__(name, value)
        else:
            raise AttributeError('Cant set attribute on an enum class')

    def __new__(mcs, name, parents, dct):
        with mcs.__unfrozen:
            aggregated = 0
            flag_values = {}
            for attr_key, attr_val in dct.items():
                if attr_key.startswith('_') or hasattr(attr_val, '__call__'):
                    continue

                if not isinstance(attr_val, int):
                    msg = 'Class member (%s) must be an integer'
                    raise TypeError(msg % attr_key)
                elif attr_val == 0:
                    msg = 'Zero is not a valid value for an enum bit'
                    raise ValueError(msg)
                elif (math.log(attr_val, 2) !=
                      math.floor(math.log(attr_val, 2))):
                    msg = 'Class member (%s) must be a power of 2'
                    raise ValueError(msg % attr_key)
                elif attr_val & aggregated > 0:
                    msg = 'Class member (%s) must be unique power of 2'
                    raise ValueError(msg % attr_key)

                aggregated |= attr_val
                flag_values[attr_val] = attr_key

            # Track the bitmast of flags which we now about
            ordered_values = OrderedDict()
            dct['__aggregated'] = aggregated
            dct['__ordered_values'] = ordered_values

            created = super(_BitEnumMeta, mcs).__new__(mcs, name, parents, dct)

            # Replace all of the class members with instances
            for int_value in sorted(flag_values.keys()):
                new_inst = created(int_value)
                setattr(created, flag_values[int_value], new_inst)
                ordered_values[int_value] = new_inst

            def _real_repr(self):
                return '%s(%s)' % (name, int.__repr__(self))
            setattr(created, '__repr__', _real_repr)

            def _real_iter(self):
                for enum_int_val, inst in ordered_values.items():
                    if int.__and__(self, enum_int_val) > 0:
                        yield inst
            setattr(created, '__iter__', _real_iter)

            # Wrap all of the comparison operators to return concrete instances
            def _return_concrete(towrap):
                def _wrapper(*args, **kwargs):
                    return created(towrap(*args, **kwargs))
                return _wrapper

            def _disable_method(method_name):
                def _inner(*args, **kwargs):
                    msg = 'Unable to call method (%s) on enum type'
                    raise NotImplementedError(msg % method_name)
                return _inner

            for parent in parents:
                if issubclass(parent, int):
                    for attr in mcs.INT_TO_WRAP:
                        try:
                            setattr(created, attr,
                                    _return_concrete(getattr(int, attr)))
                        except AttributeError as exc:
                            if attr not in mcs.PY3_REMOVED:
                                raise exc

                    for attr in mcs.INT_TO_DISABLE:
                        try:
                            setattr(created, attr, _disable_method(attr))
                        except AttributeError as exc:
                            if attr not in mcs.PY3_REMOVED:
                                raise exc

                    break  # No need to check more parent classes

            def _real_invert(self):
                bit_invert = int.__invert__(self)
                return created(bit_invert & aggregated)
            setattr(created, '__invert__', _real_invert)

            return created


@add_metaclass(_BitEnumMeta)
class BitEnum(int):
    @staticmethod
    def __contains(aggregated, value):
        return value >= 0 and (value | aggregated) <= aggregated

    def __new__(cls, value):
        aggr = cls.__dict__['__aggregated']
        if not cls.__contains(aggr, value):
            msg = 'Requested value (%s) can not be composed of known flags'
            raise ValueError(msg % value)

        try:
            # Consider using the existence test or LBYL here
            return cls.__dict__['__ordered_values'][value]
        except KeyError:
            return super(BitEnum, cls).__new__(cls, value)

    def __setattr__(self, name, value):
        raise AttributeError('Cant set attribute on an enum class instance')

    def __contains__(self, value):
        return self.__contains(self.__class__.__dict__['__aggregated'], value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return int(self) == int(other)

    def __ne__(self, other):
        if not isinstance(other, self.__class__):
            return True
        return int(self) != int(other)

    def __cmp__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('unorderable types: %s %s' %
                            (self.__class__.__name__,
                             other.__class__.__name__))
        return super(BitEnum, self).__cmp__(other)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('unorderable types: %s %s' %
                            (self.__class__.__name__,
                             other.__class__.__name__))
        return int(self) < int(other)

    def __gt__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError('unorderable types: %s %s' %
                            (self.__class__.__name__,
                             other.__class__.__name__))
        return int(self) > int(other)
