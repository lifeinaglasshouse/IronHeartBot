import os
import openai
from asgiref.sync import sync_to_async

openai.api_key = os.getenv("OPENAI_TOKEN")
acompletion = sync_to_async(openai.Completion.create)

async def completion_raw(prompt: str):
    return await acompletion(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=1562,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

async def completion(prompt: str) -> str:
    return (await completion_raw(prompt))["choices"][0]["text"]