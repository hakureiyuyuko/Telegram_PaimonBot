from typing import Coroutine
import asyncio
from defs.query_resource_points import init_point_list_and_map


def sync(coroutine: Coroutine):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coroutine)


print("初始化资源点列表和资源点映射...")
sync(init_point_list_and_map())
print("初始化完成")
