

def reformat(d, clean_func=None, clean_func_dict=None, verbose=False):
    """
    @param    d                  Dictionary                        Data to process.

    @param    clean_func         Function pointer                  Optional. If provided, each 'value' will be processed
                                                                   by this function.

    @param    clean_func_dict    Dictionary of function pointer    Optional. Takes the form of {key: function_pointer},
                                                                   where each 'value' in the CSV will be used to lookup a
                                                                   function for processing based on the key/name.

    @param    verbose            Boolean                           Used to print() debug info.
    """
    if clean_func is not None or clean_func_dict is not None:
        for k, v in d.items():
            if clean_func is not None:
                if verbose:
                    print("reformat(): Calling 'clean_func' on field: {k} -> {v}".format(k=k, v=v))

                d[k] = clean_func(v)

            if clean_func_dict is not None:
                if k in clean_func_dict:
                    if verbose:
                        print("reformat(): Calling clean function (via 'clean_func_dict') on field: {k} -> {v}".format(k=k, v=v))

                    try:
                        d[k] = clean_func_dict[k](v)

                    except Exception, e:
                        if verbose:
                            print("reformat(): ERROR: {e}".format(e=e))

    return d
