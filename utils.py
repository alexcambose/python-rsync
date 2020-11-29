def remove_dictionary_key(dictionary_array, key):
    def it(x):
        x.pop(key)
        return x
    return list(map(it, dictionary_array))