from langchain.chains.llm import LLMChain
from langchain_community.chat_models import ChatYandexGPT
from langchain_core.messages import AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    FewShotChatMessagePromptTemplate
)
from langchain.chains.sequential import SimpleSequentialChain
from langchain.chains.transform import TransformChain

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
    transform_chain_normalize = TransformChain(
        input_variables=["input"],
        output_variables=["input"],
        transform=normalize_herbicide_operation
    )
    transform_chain_aor = TransformChain(
        input_variables=["output"],
        output_variables=["output"],
        transform=assign_department
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(constants.AppConstants.SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    llm_chain = LLMChain(prompt=prompt, llm=model)
    full_chain = SimpleSequentialChain(
        chains=[transform_chain_normalize, llm_chain, transform_chain_aor],
        input_key="input",
        output_key="output",
        verbose=True
    )

    return full_chain.run(message)


def model_output_to_json(response: AIMessage):
    cleaned = re.sub(r'^```(json)?|```$', '', response.content, flags=re.MULTILINE).strip()

    return json.loads(cleaned)


def normalize_herbicide_operation(inputs: dict) -> dict:
    text = inputs["input"]
    text = re.sub(r"внесение\s+почв\w*\s+гербицид\w*", "внесение гербицидов", text, flags=re.IGNORECASE)

    return {"input": text}


def assign_department(inputs: dict) -> dict:
    import json
    import re

    raw_output = inputs["output"]

    if isinstance(raw_output, str):
        cleaned_output = re.sub(r"^```(?:json)?\n?", "", raw_output.strip(), flags=re.IGNORECASE)
        cleaned_output = re.sub(r"\n?```$", "", cleaned_output.strip())
        try:
            data = json.loads(cleaned_output)
        except json.JSONDecodeError:
            raise ValueError("Не удалось декодировать JSON. Получен текст:\n" + cleaned_output)
    else:
        data = raw_output

    aor_departments = {1, 3, 4, 5, 6, 7, 9, 10, 11, 12, 16, 17, 18, 19, 20}

    new_operations = []

    for op in data.get("операции", []):
        otd = op.get("отделение")
        if isinstance(otd, list):
            for idx, sub_otd in enumerate(otd):
                new_op = op.copy()
                new_op["отделение"] = sub_otd

                if isinstance(op.get("площадь", {}).get("за_день"), list):
                    new_op["площадь"] = {
                        "за_день": op["площадь"]["за_день"][idx],
                        "c_начала_операции": op["площадь"]["c_начала_операции"][idx]
                    }

                if not new_op.get("подразделение") and sub_otd in aor_departments:
                    new_op["подразделение"] = "АОР"

                new_operations.append(new_op)
        else:
            if otd in aor_departments and not op.get("подразделение"):
                op["подразделение"] = "АОР"
            new_operations.append(op)

    data["операции"] = new_operations
    return {"output": json.dumps(data, ensure_ascii=False)}
