from rest_framework.exceptions import MethodNotAllowed


class ModelViewSetExcludeActionMixin:
    allow_actions = []  # List of allowed actions

    def check_action_allowed(self):
        if self.allow_actions and self.action not in self.allow_actions:
            raise MethodNotAllowed(self.request.method)

    def list(self, request, *args, **kwargs):
        self.check_action_allowed()
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.check_action_allowed()
        return super().retrieve(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        self.check_action_allowed()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.check_action_allowed()
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        self.check_action_allowed()
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        self.check_action_allowed()
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        self.check_action_allowed()  # Call your custom method before creating an object
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self.check_action_allowed()  # Call your custom method before updating an object
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self.check_action_allowed()  # Call your custom method before deleting an object
        super().perform_destroy(instance)


detail_success_response = {
    202: {
        "type": "object",
        "properties": {"detail": {"type": "string", "example": "success"}},
    }
}
