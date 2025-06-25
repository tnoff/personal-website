from opentelemetry.trace import get_current_span

class OpenTelemetryEnrichMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        span = get_current_span()
        if span and span.is_recording():
            client_ip = self.get_client_ip(request)
            span.set_attribute("http.client_ip", client_ip)
            span.set_attribute("http.user_agent", request.headers.get("User-Agent", ""))
            span.set_attribute("http.referer", request.headers.get("Referer", ""))
            span.set_attribute("http.origin", request.headers.get("Origin", ""))
            # Add more headers or custom logic if needed

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR", "")