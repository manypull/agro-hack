from schemas.api_schemas import AgroResponse, AgroRequest
from fastapi import APIRouter, Depends, HTTPException
from services.run_model import YandexGPT
from app.config.config import get_settings

import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/agro",
    tags=["agro"],
)

@router.post("/process", response_model=AgroResponse)
def process_agro_message(request: AgroRequest, settings=Depends(get_settings)):
    model = YandexGPT(settings=settings)
    try:
        json_output = model.run_model(request.message)
        return AgroResponse(result=json_output)
    except Exception as e:
        logger.error("Ошибка при обработке запроса:\n%s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
