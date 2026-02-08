import csv
from typing import List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from langsmith.wrappers import wrap_openai
from openai import OpenAI


load_dotenv()  # 自动加载 .env 文件中的变量

client = wrap_openai(OpenAI())
# --- 1. 配置智谱 GLM ---
'''os.environ["OPENAI_API_KEY"] = "你的智谱API_KEY"
os.environ["OPENAI_BASE_URL"] = "https://open.bigmodel.cn/api/paas/v4/"'''

# --- 2. 定义分镜脚本的结构 ---
class Shot(BaseModel):
    shot_number: int = Field(description="镜号")
    shot_type: str = Field(description="景别，如：特写、全景、中景、俯拍等")
    content: str = Field(description="画面具体表现内容")
    audio: str = Field(description="台词、旁白或环境音效")

class Storyboard(BaseModel):
    title: str = Field(description="剧名或场景名")
    shots: List[Shot] = Field(description="分镜列表")

# --- 3. 设置解析器和提示词 ---
parser = PydanticOutputParser(pydantic_object=Storyboard)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一位资深的影视导演和分镜师。你的任务是根据用户提供的原始剧情、脚本或改写要求，"
               "生成专业、细致的分镜脚本。\n\n"
               "注意格式规范：\n{format_instructions}"),
    ("human", "请根据以下需求改写分镜脚本：\n{user_input}")
])

# --- 4. 初始化模型 (使用免费的 glm-4.7-flash) ---
model = ChatOpenAI(
    model="glm-4.7-flash",
    temperature=0.8, # 稍微高一点以保持创意
)

# --- 5. 构建 Chain ---
chain = prompt | model | parser

# --- 6. 运行智能体 ---
def read_file(file_path: str) -> str:
    """
    根据文件类型读取内容。
    支持 txt 和 csv 文件。
    """
    if file_path.endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    elif file_path.endswith('.csv'):
        content = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                content.append(', '.join(row))
        return '\n'.join(content)
    else:
        raise ValueError("仅支持 txt 和 csv 文件格式！")

async def generate_storyboard(input_data: str, is_file: bool = False):
    """
    生成分镜脚本。
    :param input_data: 用户输入的文本或文件路径。
    :param is_file: 是否为文件路径。
    """
    if is_file:
        input_data = read_file(input_data)

    print("🎬 正在创作分镜脚本...")
    input_payload = {
        "user_input": input_data,
        "format_instructions": parser.get_format_instructions()
    }

    result = await chain.ainvoke(input_payload)

    # 格式化打印输出
    print(f"\n项目名称：{result.title}")
    print("-" * 50)
    for s in result.shots:
        print(f"第 {s.shot_number} 镜 | {s.shot_type}")
        print(f"画面：{s.content}")
        print(f"声音：{s.audio}")
        print("-" * 20)

if __name__ == "__main__":
    import asyncio
    import argparse

    arg_parser = argparse.ArgumentParser(description="分镜脚本生成器")
    arg_parser.add_argument("--text", type=str, help="用户输入的文本或文件路径")
    arg_parser.add_argument("--is_file", action="store_true", help="是否为文件路径")
    args = arg_parser.parse_args()

    asyncio.run(generate_storyboard(args.text, args.is_file))
