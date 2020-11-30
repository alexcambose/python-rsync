"""
unility functions
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
