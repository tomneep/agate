import functools
import time

def cache(fn=None,time_to_live=3600): # one hour default to clear all caches
    if not fn: return functools.partial(cache,time_to_live=time_to_live)
    my_cache = {"value":{},"expires":time.time()+ time_to_live}
    def _inner_fn(*args,**kwargs):
        key = tuple(args)+tuple(kwargs) 
        if(time.time() > my_cache["expires"]):
             my_cache["value"] = {}
             my_cache["expires"] = time.time()+ time_to_live
        if key not in my_cache["value"]:
               my_cache["value"][key] = fn(*args,**kwargs)
        return my_cache["value"][key]
    return _inner_fn

