from django.utils.cache import add_never_cache_headers


class NoCacheHtmlMiddleware:
    """Las páginas no se guardan en el navegador: tras una actualización, todos ven la versión nueva.

    Los archivos estáticos no pasan por aquí (los sirve WhiteNoise con un nombre nuevo en cada versión).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.get("Content-Type", "").startswith("text/html") and not response.has_header("Cache-Control"):
            add_never_cache_headers(response)
        return response
