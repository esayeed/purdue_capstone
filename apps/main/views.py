from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db import connection


def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world! This is your Django starter.")


def health_check(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


def db_health_check(request: HttpRequest) -> JsonResponse:
    """
    Extended health check that verifies database connectivity.
    Used during Saturday's Azure SQL connectivity test.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row and row[0] == 1:
                return JsonResponse(
                    {"status": "ok", "db": "connected", "engine": connection.vendor},
                    status=200,
                )
    except Exception as e:
        return JsonResponse(
            {"status": "error", "db": "disconnected", "detail": str(e)},
            status=503,
        )
    return JsonResponse(
        {"status": "error", "db": "unknown"},
        status=503,
    )
