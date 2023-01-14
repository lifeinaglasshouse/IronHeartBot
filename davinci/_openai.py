import os
import openai
from asgiref.sync import sync_to_async

import asyncio

openai.api_key = os.getenv("OPENAI_TOKEN")
QUEUE_MAX = int(os.getenv("QUEUE_MAX"))
acompletion = sync_to_async(openai.Completion.create)
aimage = sync_to_async(openai.Image.create)

openai_queue: int = 0

queue_con = asyncio.Condition()

async def completion_raw(prompt: str, **extra_config):
    global queue_con, openai_queue
    if openai_queue >= QUEUE_MAX:
        async with queue_con:
            await queue_con.wait()
    openai_queue += 1
    r = await acompletion(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1562,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        **extra_config
    )
    openai_queue -= 1
    async with queue_con:
        queue_con.notify()
    return r

async def image_raw(prompt: str):
    global queue_con, openai_queue
    if openai_queue >= QUEUE_MAX:
        async with queue_con:
            await queue_con.wait()
    openai_queue += 1
    r = await aimage(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    openai_queue -= 1
    async with queue_con:
        queue_con.notify()
    return r

async def completion(prompt: str, **extra_config) -> str:
    return (await completion_raw(prompt, **extra_config))["choices"][0]["text"]

async def image(prompt: str) -> str:
    return (await image_raw(prompt))['data'][0]['url']