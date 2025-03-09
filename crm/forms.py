from django import forms
from .models import Account, Contact

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'name',
            'industry',
            'phone',
            'website',
            'annual_revenue',
            'description',
            'billing_address',
            'shipping_address',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('', '-- Select Industry --'),
                ('technology', 'Technology'),
                ('finance', 'Finance'),
                ('healthcare', 'Healthcare'),
                ('retail', 'Retail'),
                ('manufacturing', 'Manufacturing'),
                ('other', 'Other'),
            ]),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://'}),
            'annual_revenue': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'shipping_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean_annual_revenue(self):
        annual_revenue = self.cleaned_data.get('annual_revenue')
        if annual_revenue is not None and annual_revenue < 0:
            raise forms.ValidationError("Annual revenue cannot be negative.")
        return annual_revenue

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        return website

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email', 'phone', 'title', 'account']
        
    def __init__(self, *args, **kwargs):
        account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)
        if account:
            self.fields['account'].initial = account
            self.fields['account'].widget = forms.HiddenInput() 