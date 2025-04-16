from langchain_community.chat_models import ChatYandexGPT
from langchain_core.messages import AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

from app import constants

from pathlib import Path
import re
import json
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path('/.env'))
API_KEY = os.getenv("YANDEX_API_KEY")
MODEL_URI = os.getenv("YANDEX_MODEL_URI")

if not API_KEY or not MODEL_URI:
    raise EnvironmentError("YANDEX_API_KEY и/или YANDEX_MODEL_URI не заданы в переменных окружения.")

model = ChatYandexGPT(
    api_key=API_KEY,
    model_uri=MODEL_URI,
    temperature=0)


def run_model(message: str) -> AIMessage:
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(constants.AppConstants.SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    chain = prompt | model

    return chain.invoke({"input": message})


def model_output_to_json(response: AIMessage):
    cleaned = re.sub(r'^```(json)?|```$', '', response.content, flags=re.MULTILINE).strip()

    return json.loads(cleaned)
