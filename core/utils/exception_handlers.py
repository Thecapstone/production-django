from rest_framework.views import exception_handler as rest_exception_handler
from rest_framework.response import Response


def exception_handler(exception, context):
    handlers = {
        "ValidationError": _generic_error,
    }

    response = rest_exception_handler(exception, context)

    exception_class = exception.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exception, context, response)

    return response


def _generic_error(exception, context, response):
    res = {}
    has_data = hasattr(response, "data")
    if has_data:
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    if len(value) > 0:
                        res[key] = value[0]
                else:
                    res[key] = value
    else:
        res["summary"] = str(exception).split("\n")[0]
        res["detail"] = exception.errors(include_url=False)
        response = Response(data=res, status=500)

    response.data = res
    return response
