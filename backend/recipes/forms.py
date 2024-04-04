import re

from django import forms
from django.core.exceptions import ValidationError

from .models import Tag


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = '__all__'

    def clean_color(self):
        color = self.cleaned_data.get('color')
        pattern = r'^#[0-9a-fA-F]{6}$'
        if not bool(re.match(pattern, color)):
            raise ValidationError('Цвет должен быть в формате hex (#RRGGBB)')
        return color
