from django.http import HttpRequest, HttpResponse


def home(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hello, world! This is your Django starter.")


def health_check(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")
