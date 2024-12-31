from .models import History

class LogUserActionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Log only if the user is authenticated and it's a relevant method
        if request.user.is_authenticated and request.method in ["POST", "PUT", "DELETE"]:
            action = f"{request.method} request on {request.path}"
            History.objects.create(user=request.user, action=action)

        return response
