from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField(
        label='Select Butterfly Image',
        widget=forms.FileInput(attrs={
            'class': 'hidden', 
            'id': 'image-upload',
            'required': True
        })
    )
