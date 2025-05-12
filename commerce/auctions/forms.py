from django import forms
from .models import Listings, Category


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listings
        fields = ['title', 'description',
                  'starting_bid', 'image_url', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter Description', 'rows': 3}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Starting Bid', 'step': '0.01'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter Image URL'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
