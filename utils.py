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