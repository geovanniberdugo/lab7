class RequireOnConfirmValidatableMixin:

    confirming = False
    REQUIRED_ON_CONFIRM = []

    def clean(self):
        cleaned_data = super().clean()

        if self.confirming:
            for field in self.REQUIRED_ON_CONFIRM:
                if not cleaned_data.get(field, None):
                    self.add_error(field, 'Campo requerido')

        return cleaned_data
