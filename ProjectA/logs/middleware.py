from .models import ActionLog

class ActionLogMiddleware:

    AUTH_PATHS = {
        '/api/auth/login/': ActionLog.ActionType.LOGIN,
        '/api/auth/logout/': ActionLog.ActionType.LOGOUT,
        '/api/auth/register/': ActionLog.ActionType.REGISTER,
        '/accounts/login/': ActionLog.ActionType.LOGIN,
        '/accounts/logout/': ActionLog.ActionType.LOGOUT,
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path in self.AUTH_PATHS:
            if response.status_code in [200, 201, 204]:
                action_type = self.AUTH_PATHS[request.path]

                ActionLog.log(
                    action_type=action_type,
                    request=request,
                    description=f'{action_type.label}',
                    is_success=True
                )
            elif response.status_code >= 400:
                action_type = self.AUTH_PATHS[request.path]

                ActionLog.log(
                    action_type=action_type,
                    request=request,
                    description=f'Failed attempt: {action_type.label}',
                    is_success=False,
                    error_message=f'Status code: {response.status_code}'
                )

        return response