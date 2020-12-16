"""
utility functions
"""


def remove_dictionary_key(dictionary_array, key):
    """
    remove a key from an array of dictionaries
    """
    def it(x):
        if key in x:
            x.pop(key)
        return x
    return list(map(it, dictionary_array))

def handle_failure(log_func = print, stop_execution = True):
    """
    decorator for catching exceptions
    """
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args,**kwargs)
            except Exception as e:
                log_func('Error ', e)
                if stop_execution: raise e
        return applicator
    return decorate

def retry_function(times_number = 2):
    """
    decorator for re-running non deterministic code
    """
    def decorate(f):
        def applicator(*args, **kwargs):
            for i in range(times_number):
                try:
                    return f(*args,**kwargs)
                except Exception:
                   pass
        return applicator
    return decorate

def sort_state(state, delete_optimized = False):
    """
    sort by nesting level
    """
    def func(a):
        count = a['path'].count('/')
        return count
    return sorted(state,key=func, reverse=delete_optimized)