import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("navnote")


class PublicCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response: Response = await call_next(request)
        except Exception:
            logger.exception("请求处理异常 %s %s", request.method, request.url.path)
            raise
        try:
            if request.method == "GET" and request.url.path.startswith("/api/public/"):
                response.headers.setdefault(
                    "Cache-Control",
                    "public, max-age=30, stale-while-revalidate=120",
                )
        except Exception:
            logger.exception("设置公开接口缓存头失败")
        return response
