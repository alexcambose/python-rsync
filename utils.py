"""
utility functions
"""
from os import path
import hashlib

def remove_dictionary_key(dictionary_array, keys):
    """
    remove a key from an array of dictionaries
    """
    def it(x): 
        for key in keys:
            if key in x:
                x.pop(key)
        return x
    return list(map(it, dictionary_array))


def handle_failure(log_func=print, stop_execution=True):
    """
    decorator for catching exceptions
    """
    def decorate(f):
        def applicator(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                log_func('Error ', e)
                if stop_execution:
                    raise e
        return applicator
    return decorate


def retry_function(times_number=2):
    """
    decorator for re-running non deterministic code
    """
    def decorate(f):
        def applicator(*args, **kwargs):
            for i in range(times_number-1):
                try:
                    return f(*args, **kwargs)
                except Exception:
                    pass
            return f(*args, **kwargs)
        return applicator
    return decorate


def sort_state(state, delete_optimized=False):
    """
    sort by nesting level
    """
    def func(a):
        count = a['path'].count(path.sep)
        return count
    return sorted(state, key=func, reverse=delete_optimized)


def create_hash(file):
    """
    create file hash
    """
    BUF_SIZE = 65536 
    sha1 = hashlib.sha1()

    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest();