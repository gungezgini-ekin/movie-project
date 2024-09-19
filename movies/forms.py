from django.contrib.auth.models import User
from django.forms import ModelForm

from django import forms
from .models import Movie, Review


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control',
                                               'placeholder': 'Give a rating (integer) to this movie between 1 and 10'})
            , 'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter a review'}),
        }



