import logging
import os
import traceback

from django.http import HttpResponse


class ErrorMiddleware:
    async_capable = True

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        response = self._get_response(request)
        return response

    def process_exception(self, request, exception):
        if not os.environ.get('DEBUG', default=0):
            if exception:
                message = '{url} | {error} | {tb}'.format(
                    url=request.build_absolute_uri(),
                    error=repr(exception),
                    tb=traceback.format_exc()
                )
                logger = logging.getLogger(request)
                logger.error(message)
            return HttpResponse("Error processing the request.", status=500)
