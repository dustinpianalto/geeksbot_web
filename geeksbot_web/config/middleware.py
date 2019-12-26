from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class AWSELBHealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META("PATH_INFO") == '/hostcheck/':
            return HttpResponse("It's Alive!")
