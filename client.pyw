import asyncio
import json
import websockets
import mss
import ctypes
import pyautogui
from PIL import Image
import io
from time import time

def timer_func(func):
    # This function shows the execution time of 
    # the function object passed
    async def wrap_func(*args, **kwargs):
        t1 = time()
        result = await func(*args, **kwargs)
        t2 = time()
        # print(f'Function {func.__name__!r} executed in {(t2-t1):.4f}s')
        return result
    return wrap_func

user32 = ctypes.windll.user32
WIDTH , HEIGHT = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

async def handler(websocket):
    await asyncio.gather(
        producer(websocket),
        consumer(websocket),
    )

async def consumer(websocket):
    global task
    async for message in websocket:
        parsed = json.loads(message)
        if parsed.get('type') == "toggle":
            if task.done():
                task = asyncio.create_task(send_ss(websocket))    
            else:
                task.cancel()

        if parsed.get('type') == "click":
            pyautogui.click(parsed.get('x'), parsed.get('y'))

        elif parsed.get('type') == "keydown":
            pyautogui.keyDown(parsed.get('key'))


        elif parsed.get('type') == "keyup":
            pyautogui.keyUp(parsed.get('key'))
   
async def send_ss(web):
    with mss.mss() as sct:
        while True:
                ss = await retreive_screenshot(sct)
                await web.send(ss)

async def producer(websocket):
    global task
    task = asyncio.create_task(send_ss(websocket))
    task.cancel()

async def start_client():
    async with websockets.connect("wss://RAD.len1911.repl.co") as websocket:
        await handler(websocket)

@timer_func
async def retreive_screenshot(sct):

        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}
        img = sct.grab(rect)
        raw_bytes = mss.tools.to_png(img.rgb, img.size)
       
        return await compress_img(raw_bytes)

        # return raw_bytes

async def compress_img(raw): # make better in future
        
        rawio = io.BytesIO(raw)

        image = Image.open(rawio)
        image = image.convert("P", palette=Image.ADAPTIVE, colors=256)

        temp = io.BytesIO()
        image.save(temp, optimize=True, format="png")

        return temp.getvalue()

    
asyncio.run(start_client())