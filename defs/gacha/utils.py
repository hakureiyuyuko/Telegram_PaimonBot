import datetime
import functools
import inspect
import json
import os
from sqlitedict import SqliteDict


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dict_obj):
    if not isinstance(dict_obj, dict):
        return dict_obj
    inst = Dict()
    for k, v in dict_obj.items():
        inst[k] = dict_to_object(v)
    return inst


def filter_list(plist, func):
    return list(filter(func, plist))


def init_db(db_dir, db_name) -> SqliteDict:
    return SqliteDict(os.path.join(db_dir, db_name),
                      encode=json.dumps,
                      decode=json.loads,
                      autocommit=True)


def cache(ttl=datetime.timedelta(hours=1), **kwargs):
    def wrap(func):
        cache_data = {}

        @functools.wraps(func)
        async def wrapped(*args, **kw):
            nonlocal cache_data
            bound = inspect.signature(func).bind(*args, **kw)
            bound.apply_defaults()
            ins_key = '|'.join(['%s_%s' % (k, v) for k, v in bound.arguments.items()])
            default_data = {"time": None, "value": None}
            data = cache_data.get(ins_key, default_data)

            now = datetime.datetime.now()
            if not data['time'] or now - data['time'] > ttl:  # noqa
                try:
                    data['value'] = await func(*args, **kw)
                    data['time'] = now  # noqa
                    cache_data[ins_key] = data
                except Exception as e:
                    raise e

            return data['value']

        return wrapped

    return wrap
