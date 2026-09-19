from django import forms
from .models import Plant


class PlantForm(forms.ModelForm):
    """Форма для добавления/редактирования растения"""

    class Meta:
        model = Plant
        fields = ['name', 'min_humidity', 'max_humidity', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Монстера',
            }),
            'min_humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
            }),
            'max_humidity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        labels = {
            'name': 'Название растения',
            'min_humidity': 'Минимальная влажность (%)',
            'max_humidity': 'Максимальная влажность (%)',
            'is_active': 'Активно',
        }

    def clean(self):
        cleaned_data = super().clean()
        min_h = cleaned_data.get('min_humidity')
        max_h = cleaned_data.get('max_humidity')

        if min_h is not None and max_h is not None:
            if min_h >= max_h:
                raise forms.ValidationError(
                    'Минимальная влажность должна быть меньше максимальной'
                )

        return cleaned_data