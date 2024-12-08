import os
import tempfile
import time

from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.responses import JSONResponse

from src import log
from src.whisper_service import WhisperService


app = FastAPI(title="ASR Inference Service")

asr_router = APIRouter(prefix="/whisper", tags=["Whisper ASR Inference"])

# Setting default inference regime to HuggingFace model
whisper_asr = WhisperService()


@asr_router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """
    """
    # Creating a temporary .WAV file for
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        log.info("Temporary file creation")
        temp_file.write(await file.read())
        temp_file_path = temp_file.name
        log.info(f"Temporary file {temp_file_path} created")

    try:
        # Using one of pre-defined services (WhisperService, OpenVinoService, InferenceService) for ASR
        start = time.time()
        transcription = await whisper_asr.transcribe(temp_file_path)
        end = time.time()
        log.info("Transcription completed")
        return JSONResponse(content={"text": transcription, "time": str(end - start)})
    except Exception as e:
        log.error(f"Error during transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during transcription: {str(e)}")
    finally:
        log.info(f"Removing temporary file {temp_file_path}")
        os.remove(temp_file_path)


app.include_router(asr_router)