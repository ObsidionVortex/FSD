from django import forms
from .models import Product


# PRODUCT FORM
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'stock',
            'image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Minimalist Everyday Canvas Backpack',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Describe materials, craftsmanship, dimensions, and everyday use...',
                'rows': 4,
                'required': True,
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Available inventory count',
                'min': '0',
                'required': True,
            }),
            'image': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://images.unsplash.com/...',
            }),
        }


# CHECKOUT FORM
class CheckoutForm(forms.Form):
    address = forms.CharField(
        min_length=10,
        widget=forms.Textarea(attrs={
            'class': 'form-input form-textarea',
            'placeholder': 'Enter street address, flat / suite number, city, state, postal code, and contact phone...',
            'rows': 3,
            'required': True,
        }),
        label='Shipping & Delivery Address'
    )
