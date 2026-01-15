from .models import ActionLog


class LoggingMixin:

    log_action_type = ActionLog.ActionType.OTHER
    log_on_success = True
    log_on_failure = True

    def get_log_description(self):
        return ''

    def get_log_object(self):
        if hasattr(self, 'object'):
            return self.object
        return None

    def get_log_extra_data(self):
        return {}

    def log_action(self, is_success=True, error_message=''):
        if is_success and not self.log_on_success:
            return
        if not is_success and not self.log_on_failure:
            return

        ActionLog.log(
            action_type=self.log_action_type,
            request=self.request,
            obj=self.get_log_object(),
            description=self.get_log_description(),
            extra_data=self.get_log_extra_data(),
            is_success=is_success,
            error_message=error_message
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        self.log_action(is_success=True)
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        self.log_action(
            is_success=False,
            error_message=str(form.errors)
        )
        return response


class CreateLoggingMixin(LoggingMixin):

    def get_log_description(self):
        if self.object:
            return f'Updated {self.object.__class__.__name__}: {self.object}'
        return 'Added new object'


class UpdateLoggingMixin(LoggingMixin):

    def get_log_description(self):
        if self.object:
            return f'Updated {self.object.__class__.__name__}: {self.object}'
        return 'Updated object'


class DeleteLoggingMixin(LoggingMixin):

    _deleted_object_repr = None

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self._deleted_object_repr = str(self.object)
        response = super().delete(request, *args, **kwargs)
        self.log_action(is_success=True)
        return response

    def get_log_description(self):
        return f'Deleted: {self._deleted_object_repr}'