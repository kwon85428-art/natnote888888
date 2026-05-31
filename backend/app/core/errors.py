"""统一 HTTP 异常响应（FastAPI 推荐：客户端以 detail 字段为准）。"""

from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("navnote")

_AUTH_PREFIX = "/api/auth"


def _detail_json(status_code: int, detail: object) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return _detail_json(exc.status_code, exc.detail)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    if request.url.path.startswith(_AUTH_PREFIX):
        return _detail_json(400, "请求无效")
    return _detail_json(422, exc.errors())


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("未处理异常 %s %s", request.method, request.url.path, exc_info=exc)
    return _detail_json(500, "服务器内部错误")
