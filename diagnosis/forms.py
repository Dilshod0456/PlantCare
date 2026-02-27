from django import forms
from .models import PlantImage

class PlantImageForm(forms.ModelForm):
    class Meta:
        model = PlantImage
        fields = ['image']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-eco-green file:text-white hover:file:bg-eco-dark-green',
                'accept': 'image/*'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].label = "O'simlik rasmi"
        self.fields['image'].help_text = "JPG, PNG formatdagi rasm yuklang (max 10MB)"
