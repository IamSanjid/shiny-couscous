import os
import pathlib
import xml.etree.ElementTree as ET
from enum import Enum
from typing import Dict
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models.base import BaseLanguageModel
from langchain.messages import HumanMessage, AIMessage, SystemMessage

PROMPTS_DIR = "prompts"

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

class Models(Enum):
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GPT_4o_MINI = "gpt-4o-mini"

models: Dict[Models, BaseLanguageModel] = {
    Models.GEMINI_2_5_FLASH: GoogleGenerativeAI(model=Models.GEMINI_2_5_FLASH.value),
    Models.GPT_4o_MINI: ChatOpenAI(model=Models.GPT_4o_MINI.value)
}

class Contact(BaseModel):
    name: str | None = Field(description="The name of the contact")
    phone: str | None = Field(description="The phone of the contact")
    email: str | None = Field(description="The email of the contact")

parser = PydanticOutputParser(pydantic_object=Contact)

base_conversation = [
    SystemMessage(content=_get_system()),
    *_get_user_ai_conversation(),
]

def parse_contact_info(text: str, model: Models = Models.GEMINI_2_5_FLASH) -> Contact:
    prompt = [
        *base_conversation,
        HumanMessage(text)
    ]
    chain = models[model] | parser
    return chain.invoke(prompt)

async def aparse_contact_info(text: str, model: Models = Models.GEMINI_2_5_FLASH) -> Contact:
    prompt = [
        *base_conversation,
        HumanMessage(text)
    ]
    chain = models[model] | parser
    return await chain.ainvoke(prompt)

if __name__ == "__main__":
    text = input("Extract info: ")
    print(parse_contact_info(text, Models.GPT_4o_MINI))
