import argparse
import json
from typing import AsyncGenerator

from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse, PlainTextResponse
import uvicorn

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
from vllm.utils import random_uuid

from .config import *

TIMEOUT_KEEP_ALIVE = 5  # seconds.
TIMEOUT_TO_PREVENT_DEADLOCK = 1  # seconds.
app = FastAPI()


@app.post("/generate")
async def generate(request: Request) -> Response:
    """Generate completion for the request.

    The request should be a JSON object with the following fields:
    - prompt: the prompt to use for the generation.
    - stream: whether to stream the results or not.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    try:
        request_dict = await request.json()
        prompt = request_dict.pop("prompt")
        stream = False
        sampling_params = SamplingParams(max_tokens = MAX_TOKENS, 
                                         top_p = TOP_P, 
                                         temperature = TEMPERATURE, 
                                         use_beam_search=False)
        request_id = random_uuid()
        results_generator = engine.generate(prompt, sampling_params, request_id)

        # Streaming case
        #async def stream_results() -> AsyncGenerator[bytes, None]:
        #    async for request_output in results_generator:
        #        prompt = request_output.prompt
        #        text_outputs = [
        #            prompt + output.text for output in request_output.outputs
        #        ]
        #        ret = {"text": text_outputs}
        #        yield (json.dumps(ret) + "\0").encode("utf-8")

        #async def abort_request() -> None:
        #    await engine.abort(request_id)

        #if stream:
        #    background_tasks = BackgroundTasks()
        #    # Abort the request if the client disconnects.
        #    background_tasks.add_task(abort_request)
        #    return StreamingResponse(stream_results(), background=background_tasks)

        # Non-streaming case
        final_output = None
        async for request_output in results_generator:
            if await request.is_disconnected():
                # Abort the request if the client disconnects.
                await engine.abort(request_id)
                return Response(status_code=499)
            final_output = request_output

        assert final_output is not None
        prompt = final_output.prompt
        text_outputs = [output.text for output in final_output.outputs]
        print("@@@@@")
        print(text_outputs)
        return PlainTextResponse(text_outputs[0])
    except Exception as e:
        err_msg = "vllm server error! {}".format(str(e))
        print(err_msg)
        return PlainTextResponse(err_msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser = AsyncEngineArgs.add_cli_args(parser)
    parser.set_defaults(model=MODEL_PATH)
    args = parser.parse_args()

    engine_args = AsyncEngineArgs.from_cli_args(args)
    engine = AsyncLLMEngine.from_engine_args(engine_args)

    uvicorn.run(app,
                host=MODEL_SERVER_IP,
                port=MODEL_SERVER_PORT,
                log_level="debug",
                timeout_keep_alive=TIMEOUT_KEEP_ALIVE)
