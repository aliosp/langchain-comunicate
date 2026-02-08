from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio

# 导入现有的逻辑
from story_board import generate_storyboard, chain
from chat import run_weather_agent

app = FastAPI(title="LangChain Communicate API")

# 数据模型
class StoryboardRequest(BaseModel):
    user_input: str

class ChatRequest(BaseModel):
    message: str

# 挂载静态文件
os.makedirs("static", exist_ok=True)

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

@app.post("/api/storyboard")
async def api_generate_storyboard(req: StoryboardRequest):
    try:
        # 我们需要捕获原本直接打印到控制台的内容，或者直接调用 chain
        input_payload = {
            "user_input": req.user_input,
            "format_instructions": chain.steps[-1].get_format_instructions()
        }
        result = await chain.ainvoke(input_payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    try:
        answer = await run_weather_agent(req.message)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
