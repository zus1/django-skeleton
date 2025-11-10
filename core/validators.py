from django.core.exceptions import ValidationError

class PasswordContainsUpperCaseValidator:
    def validate(self, password, user=None):
        upper_count = 0
        for char in password:
            if char.isupper():
                upper_count += 1

        if upper_count == 0:
            raise ValidationError(message="Password must contain at least one uppercase character")

    def get_help_text(self):
        return "Password must contain at least one upper case character"


class PasswordContainsSpecialCharValidator:
    def validate(self, password, user=None):

        sc_count = 0
        for char in password:
            if not char.isalnum():
                sc_count += 1

        if sc_count == 0:
            raise ValidationError(message="Password must contain at least one special character")

    def get_help_text(self):
        return "Password must contain at least one special character"

class PasswordContainsNumericValidator:
    def validate(self, password, user=None):
        num_count = 0
        for char in password:
            if char.isnumeric():
                num_count += 1

        if num_count == 0:
            raise ValidationError(message="Password must contain at least one numeric character")


    def get_help_text(self):
        return "Password must contain at least one numeric character"
