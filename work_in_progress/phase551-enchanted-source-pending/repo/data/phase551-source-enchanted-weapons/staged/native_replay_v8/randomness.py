"""Direct primitive tape; synthetic Python RNG is not native-law verified."""
from dataclasses import dataclass
import random
import re
import struct
import math


def _bits(value):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError('finite float required')
    return struct.pack('>d', float(value)).hex()


def _float(bits):
    if type(bits) is not str or re.fullmatch('[0-9a-f]{16}', bits) is None:
        raise ValueError('invalid direct primitive BE64')
    value = struct.unpack('>d', bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise ValueError('nonfinite primitive')
    return value


def _uint32_contract(label, context, ordinal, width):
    if (type(context) is not str or re.fullmatch(r'fraction_shuffle:[PO]:(?:0|[1-9][0-9]*):[PO]:(?:direct|multiply|remove|steal)',context) is None
            or type(ordinal) is not int or not 0<=ordinal<=5 or type(width) is not int or width!=7-ordinal
            or label!=f'{context}:{ordinal}:{width}'):
        raise ValueError('invalid fixed-seven global primitive context')


class SeededRandom:
    alignment = 'independent_python_synthetic_not_native_distribution_verified'
    def __init__(self, seed=0):
        self.generator=random.Random(seed);self.audit=[];self.seed=seed
    def randf(self,label):
        value=self.generator.random();self.audit.append(dict(kind='randf',label=label,args=[],value_bits=_bits(value)));return value
    def randf_range(self,label,low,high):
        value=self.generator.uniform(low,high);self.audit.append(dict(kind='randf_range',label=label,args=[_bits(low),_bits(high)],value_bits=_bits(value)));return value
    def randi_range(self,label,low,high):
        if type(low) is not int or type(high) is not int:raise ValueError('integer endpoints required')
        value=self.generator.randint(min(low,high),max(low,high));self.audit.append(dict(kind='randi_range',label=label,args=[low,high],value=value));return value
    def global_u32(self,label,context,ordinal,width):
        _uint32_contract(label,context,ordinal,width);value=self.generator.getrandbits(32)
        self.audit.append(dict(kind='global_u32',label=label,args=[],value=value,context=context,ordinal=ordinal,width=width));return value


class TapeRandom:
    alignment='conditional_direct_native_primitive_returns'
    def __init__(self, records):
        if type(records) is not list:raise ValueError('primitive tape must be array')
        from copy import deepcopy
        self.records=deepcopy(records);self.position=0;self.audit=[]
        for row in self.records:self._validate(row)
    @staticmethod
    def _validate(row):
        if type(row) is not dict or type(row.get('label')) is not str or not row['label']:raise ValueError('invalid primitive label')
        kind=row.get('kind');fields={'kind','label','args'}
        if kind in ('randf','randf_range'):
            if set(row)!=fields|{'value_bits'}:raise ValueError('unknown float primitive fields')
            if type(row['args'])is not list or len(row['args'])!=(0 if kind=='randf'else 2):raise ValueError('bad float args')
            args=[_float(x)for x in row['args']];value=_float(row['value_bits']);low,high=(0.0,1.0)if not args else(min(args),max(args))
            if not low<=value<=high:raise ValueError('primitive return outside bounds')
        elif kind=='randi_range':
            if set(row)!=fields|{'value'}or type(row['args'])is not list or len(row['args'])!=2:raise ValueError('bad integer fields')
            if any(type(v)is not int or not -(2**31)<=v<2**31 for v in row['args'])or type(row['value'])is not int or not min(row['args'])<=row['value']<=max(row['args']):raise ValueError('bad integer primitive')
        elif kind=='global_u32':
            if set(row)!=fields|{'value','context','ordinal','width'}or row['args']!=[]or type(row['value'])is not int or not 0<=row['value']<=4294967295:raise ValueError('bad global uint32')
            _uint32_contract(row['label'],row['context'],row['ordinal'],row['width'])
        else:raise ValueError('unknown direct primitive kind; old uniform/integer tapes are historical')
    def _take(self,kind,label,args,extra=None):
        if self.position>=len(self.records):raise ValueError('primitive tape exhausted: '+label)
        row=self.records[self.position]
        for key,value in dict(kind=kind,label=label,args=args,**(extra or {})).items():
            if type(row.get(key))is not type(value)or row[key]!=value:raise ValueError('primitive tape mismatch at '+str(self.position)+':'+key)
        self.position+=1;self.audit.append(dict(row));return _float(row['value_bits'])if'value_bits'in row else row['value']
    def randf(self,label):return self._take('randf',label,[])
    def randf_range(self,label,low,high):return self._take('randf_range',label,[_bits(low),_bits(high)])
    def randi_range(self,label,low,high):
        if type(low)is not int or type(high)is not int:raise ValueError('integer endpoints required')
        return self._take('randi_range',label,[low,high])
    def global_u32(self,label,context,ordinal,width):
        _uint32_contract(label,context,ordinal,width)
        return self._take('global_u32',label,[],dict(context=context,ordinal=ordinal,width=width))
    def assert_consumed(self):
        if self.position!=len(self.records):raise ValueError('unconsumed direct primitive tape')


@dataclass
class BalancedRng:
    expected_wins: float = 0.0
    wins: int = 0
    balancedness: float = 3.0
    last_result: bool = False

    def reset(self, bias=0.0):
        self.expected_wins, self.wins, self.last_result = bias, 0, False

    def roll(self, target, random_source, label):
        if target <= 0:
            return False
        if target >= 1:
            return True
        chance = target
        difference = self.expected_wins - self.wins
        if difference > 0.3:
            chance *= self.balancedness * min(1.0, difference)
        elif difference < -0.3:
            chance /= self.balancedness * min(1.0, -difference)
        self.expected_wins += target
        if self.last_result and target < 0.4:
            chance *= 0.5
        elif not self.last_result and target > 0.6:
            chance *= 2.0
        self.last_result = random_source.randf(label) <= chance
        if self.last_result:
            self.wins += 1
        return self.last_result

    def roll_percent(self, target, random_source, label):
        return self.roll(target / 100.0, random_source, label)


@dataclass
class BalancedRange:
    acc: float = 0.0

    def draw(self, low, high, random_source, label):
        value = random_source.randi_range(label, low, high)
        difference = value - 0.5 * (low + high)
        if self.acc >= 1:
            malus = min(value - low, int(self.acc))
            self.acc -= malus
            value -= malus
        elif self.acc <= -1:
            bonus = min(high - value, int(abs(self.acc)))
            self.acc += bonus
            value += bonus
        self.acc += difference
        return value
