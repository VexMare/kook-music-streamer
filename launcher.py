import os
import sys

# 动态加载config.py到全局命名空间
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
with open(config_path, 'r', encoding='utf-8') as f:
    code = compile(f.read(), config_path, 'exec')
    exec(code, globals())

import kookvoice_bot_runtime
import asyncio

# 自动启动主循环
if hasattr(kookvoice_bot_runtime, "bot") and hasattr(kookvoice_bot_runtime, "kookvoice"):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        kookvoice_bot_runtime.bot.start(),
        kookvoice_bot_runtime.kookvoice.start()
    )) 