from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from utils import codes, messages, string_utils


def json_response():
    """
    Decorator that wraps response into json.
    """
    def decorator(func):

        @wraps(func)
        def inner(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                if not ('code' in response):
                    response['code'] = codes.OK
            except ObjectDoesNotExist as e:
                response = code_response(code=codes.BAD_REQUEST,
                                         message=messages.NOT_FOUND,
                                         error=str(e))
            except Exception as e:
                # TODO: add logger
                response = code_response(codes.SERVER_ERROR, error=str(e))
            return JsonResponse(response)
        return inner
    return decorator


def code_response(code, message=None, error=None, field=None):
    result = {'code': code}
    if message:
        message = message.copy()
        result['message'] = message
        if field:
            for k, v in result['message'].items():
                result['message'][k] = v + " " + field
    if error:
        result['error'] = error
    return result


def required_parameters(parameters_list):
    """
    Decorator to make a view only accept request with required parameters.
    :param parameters_list: list of required parameters.
    """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method == "POST":
                for parameter in parameters_list:
                    if len(parameter) >= 3 and parameter[-2:] == "[]":
                        list_parameter = parameter[:-2]
                    else:
                        list_parameter = parameter
                    value = string_utils.empty_to_none(request.POST.get(parameter) or request.FILES.get(parameter) or
                                                       request.POST.get(list_parameter) or request.FILES.get(list_parameter))
                    if value is None:
                        return code_response(code=codes.BAD_REQUEST,
                                             message=messages.MISSING_REQUIRED_PARAMS,
                                             field=parameter)
            else:
                for parameter in parameters_list:
                    if len(parameter) >= 3 and parameter[-2:] == "[]":
                        list_parameter = parameter[:-2]
                    else:
                        list_parameter = parameter
                    value = string_utils.empty_to_none(request.GET.get(list_parameter) or request.POST.get(list_parameter))
                    if value is None:
                        return code_response(code=codes.BAD_REQUEST,
                                             message=messages.MISSING_REQUIRED_PARAMS, field=list_parameter)

            return func(request, *args, **kwargs)
        return inner
    return decorator

