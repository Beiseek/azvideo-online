"""
Forms for users app.
"""
from django import forms
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля."""
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

