import asyncio
import os
import logging
from kookvoice.kookvoice import Player as OrigPlayer

class PlayerDebug(OrigPlayer):
    async def main(self):
        start_event = asyncio.Event()
        task1 = asyncio.create_task(self.push())
        task2 = asyncio.create_task(self.keepalive())
        task3 = asyncio.create_task(self.stop(start_event))

        done, pending = await asyncio.wait(
            [task1, task2],
            return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()
        start_event.set()
        await task3

    async def push(self):
        # ... 省略前置逻辑 ...
        # 只修改ffmpeg子进程部分
        command = '你的ffmpeg命令...'
        p = await asyncio.create_subprocess_shell(
            command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.PIPE
        )
        # 捕获stderr日志
        async def log_ffmpeg_stderr():
            with open('ffmpeg_debug.log', 'wb') as f:
                while True:
                    line = await p.stderr.readline()
                    if not line:
                        break
                    f.write(line)
        asyncio.create_task(log_ffmpeg_stderr())
        # ... 其余逻辑保持不变 ... 