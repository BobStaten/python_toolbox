import gc
import weakref
from garlicsim.general_misc.sleek_refs import (SleekCallArgs,
                                               SleekRef,
                                               CuteSleekValueDictionary)

from .shared import _is_weakreffable, A, counter
        
        
def test_cute_sleek_value_dictionary():
    volatile_things = [A(), 1, 4.5, 'meow', u'woof', [1, 2], (1, 2), {1: 2},
                       set([1, 2, 3])]
    unvolatile_things = [A.s, __builtins__, list, type,  list.append, str.join,
                         sum]
    
    # Using len(csvd) as our key; Just to guarantee we're not running over an
    # existing key.
        
    csvd = CuteSleekValueDictionary(counter)
    
    while volatile_things:
        volatile_thing = volatile_things.pop()
        if _is_weakreffable(volatile_thing):
            csvd[len(csvd)] = volatile_thing
            count = counter()
            del volatile_thing
            gc.collect()
            assert counter() == count + 2
        else:
            csvd[len(csvd)] = volatile_thing
            count = counter()
            del volatile_thing
            gc.collect()
            assert counter() == count + 1

            
    while unvolatile_things:
        unvolatile_thing = unvolatile_things.pop()
        csvd = CuteSleekValueDictionary(counter)
        
        csvd[len(csvd)] = unvolatile_thing
        count = counter()
        del unvolatile_thing
        gc.collect()
        assert counter() == count + 1
        
        
def test_cute_sleek_value_dictionary_one_by_one():
    volatile_things = [A(), 1, 4.5, 'meow', u'woof', [1, 2], (1, 2), {1: 2},
                       set([1, 2, 3])]
    unvolatile_things = [A.s, __builtins__, list, type,  list.append, str.join,
                         sum]
    
    # Using len(csvd) as our key; Just to guarantee we're not running over an
    # existing key.
        
    while volatile_things:
        volatile_thing = volatile_things.pop()
        csvd = CuteSleekValueDictionary(counter)
        if _is_weakreffable(volatile_thing):
            csvd[len(csvd)] = volatile_thing
            count = counter()
            del volatile_thing
            gc.collect()
            assert counter() == count + 2
        else:
            csvd[len(csvd)] = volatile_thing
            count = counter()
            del volatile_thing
            gc.collect()
            assert counter() == count + 1
            
    while unvolatile_things:
        unvolatile_thing = unvolatile_things.pop()
        csvd = CuteSleekValueDictionary(counter)
        
        csvd[len(csvd)] = unvolatile_thing
        count = counter()
        del unvolatile_thing
        gc.collect()
        assert counter() == count + 1
        