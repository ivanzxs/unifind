from django import forms
from .models import Claim


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your answer to the verification question...'
            }),
        }
        labels = {
            'answer_text': 'Your Answer',
        }
