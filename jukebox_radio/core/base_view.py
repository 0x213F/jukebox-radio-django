from django.core.serializers import serialize
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseForbidden, HttpResponseRedirect,
                         JsonResponse)
from django.template.response import TemplateResponse
from django.views import View


class BaseView(View):
    """
    Inherits from Django View.
    """

    def http_response_200(self, response):
        """
        SUCCESS
        """
        if type(response) == dict:
            return JsonResponse(response)
        if type(response) == list:
            return JsonResponse(serialize("json", response), safe=False)
        return JsonResponse(serialize("json", [response])[1:-1], safe=False)

    def http_response_400(self, message):
        """
        BAD REQUEST
        """
        return HttpResponseBadRequest(message)

    def http_response_403(self, message):
        """
        FORBIDDEN
        """
        return HttpResponseForbidden(message)

    # def http_response_422(self, message):
    #     '''
    #     INVALID FORMAT
    #     '''
    #     return HttpResponse(status_code=422, message=message)

    def template_response(self, request, template, context={}):
        return TemplateResponse(request, template, context)

    def redirect_response(self, redirect_path):
        return HttpResponseRedirect(redirect_path)
