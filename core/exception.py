from rest_framework.exceptions import ValidationError


class NotVerboseValidationError(ValidationError):
    def __str__(self):
        return self.detail[0]