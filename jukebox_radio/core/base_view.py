from django.core.serializers import serialize
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseRedirect,
    JsonResponse,
)
from django.template.response import TemplateResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


class BaseView(APIView):
    """
    Inherits from Django View.

    Note: This may not be a great pattern, but it was the quickest path forward
          during this project's genesis. PRs are accepted if you have a better
          way to handle this.
    """

    permission_classes = (IsAuthenticated,)

    def param(self, request, key):
        """
        Trying to get the parameters from a Django HTTP request can be a
        headache. This makes things a little easier.
        """
        if request.method == "GET":
            obj = request.GET
        elif request.method == "POST":
            obj = request.POST
        else:
            raise ValueError("Unsupported request method")

        val = obj[key]
        if val == "null":
            return None
        if val == "undefined":
            return None
        if val == "true":
            return True
        if val == "false":
            return False
        return val

    def http_react_response(self, _type, payload):
        """
        This is a simple interface that allows data to be piped directly into
        React Redux's dispatcher.
        """
        response = {
            "system": {
                "status": 200,
                "message": "Ok",
            },
            "redux": {
                "type": _type,
                "payload": payload,
            },
        }
        return JsonResponse(response)

    def http_response_200(self, data=None):
        """
        The main interface that returns a 200 server response with some extra
        goodies baked in.
        """
        response = {
            "system": {
                "status": 200,
                "message": "Ok",
            },
        }
        if data is not None:
            response["data"] = data
        if type(response) == dict:
            return JsonResponse(response)
        if type(response) == list:
            return JsonResponse(serialize("json", response), safe=False)
        return JsonResponse(serialize("json", [response])[1:-1], safe=False)

    def http_response_400(self, message):
        """
        BAD REQUEST
        """
        return JsonResponse(
            {
                "system": {
                    "status": 400,
                    "message": message,
                },
            },
            status=400,
        )

    def http_response_403(self, message):
        """
        FORBIDDEN
        """
        return HttpResponseForbidden(message)

    def http_response_422(self, message):
        """
        INVALID FORMAT
        """
        return HttpResponse(status_code=422, message=message)

    def template_response(self, request, template, context={}):
        return TemplateResponse(request, template, context)

    def redirect_response(self, redirect_path):
        return HttpResponseRedirect(redirect_path)
