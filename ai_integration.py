import os
import pathlib
from enum import Enum
import xml.etree.ElementTree as ET
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers.json import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

PROMPTS_DIR = "prompts"

class Models(Enum):
    GEMINI_2_5_FLASH = "google_genai:gemini-2.5-flash"
    GPT_4o_MINI = "gpt-4o-mini"

def _get_system() -> str:
    SYSTEM_FILE_NAMES = [
        "system.md",
        "system",
        "system.txt",
    ]
    system_file: pathlib.Path
    for f in SYSTEM_FILE_NAMES:
        system_file = pathlib.Path(os.path.join(PROMPTS_DIR, f))
        if system_file.is_file():
            break
    else:
        raise FileNotFoundError("system file not found in '" + PROMPTS_DIR + "'")
    
    with open(system_file, encoding='utf-8', mode='r') as f:
            return f.read()

def _get_user_ai_conversation() -> list:
    FILE_NAMES = [
        "prompt_{0}.md",
        "prompt_{0}"
        "prompt_{0}.txt"
    ]
    result = []
    current_prompt = 1
    while True:
        file_path: pathlib.Path
        for f in FILE_NAMES:
            file_path = pathlib.Path(os.path.join(PROMPTS_DIR, f.format(current_prompt)))
            if file_path.is_file():
                break
        else:
            break

        current_prompt += 1
        with open(file_path, encoding='utf-8', mode='r') as f:
            content = f.read().strip()
            if not content.startswith("<prompt>"):
                content = "<prompt>" + content
            if not content.endswith("</prompt>"):
                content = content + "</prompt>"

            try:
                root = ET.fromstring(content)
                user_prompt = root.find("user")
                ai_prompt = root.find("ai")

                if user_prompt is None or ai_prompt is None:
                    continue

                result.append(HumanMessage(user_prompt.text))
                result.append(AIMessage(ai_prompt.text))
            except:
                pass
    
    return result


models = {}
models[Models.GEMINI_2_5_FLASH] = init_chat_model("google_genai:gemini-2.5-flash")
models[Models.GPT_4o_MINI] = init_chat_model("gpt-4o-mini")
parser = JsonOutputParser()

base_conversation = [
    SystemMessage(content=_get_system()),
    *_get_user_ai_conversation(),
]

def parse_contact_info(text: str, model: Models = Models.GEMINI_2_5_FLASH):
    conversation = base_conversation.copy()
    conversation.append(HumanMessage(text))
    return parser.parse(models[model].invoke(conversation).content)

if __name__ == "__main__":
    text = input("Extract info: ")
    print(parse_contact_info(text))
