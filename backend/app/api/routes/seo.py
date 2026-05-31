from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response
from starlette.requests import Request

from app.api.deps import DbSession
from app.core.config import settings
from app.services.seo_sitemap import build_robots_txt, build_sitemap_xml, resolve_public_base_url

router = APIRouter(tags=["seo"])


def _base_from_request(request: Request) -> str:
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
    return resolve_public_base_url(
        configured=settings.public_site_url,
        request_scheme=str(scheme),
        request_host=str(host),
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt(request: Request):
    base = _base_from_request(request)
    return PlainTextResponse(build_robots_txt(base), media_type="text/plain; charset=utf-8")


@router.get("/sitemap.xml")
def sitemap_xml(request: Request, db: DbSession):
    base = _base_from_request(request)
    xml = build_sitemap_xml(db, base)
    return Response(content=xml, media_type="application/xml; charset=utf-8")
