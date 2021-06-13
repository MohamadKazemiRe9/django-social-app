from django import forms
from .models import Image
from django.utils.text import slugify
from urllib import request
from django.core.files.base import ContentFile

class ImageCreateForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('title','description','url')
        # widgets = {
        #     'url':forms.HiddenInput
        # }

    def clean_url(self):
        url = self.cleaned_data['url']
        valid_extentions = ['jpg','jpeg']
        extention = url.rsplit('.',1)[1].lower()
        if extention not in valid_extentions:
            raise forms.ValidationError('url is not correct!')
        return url
    
    def save(self,force_insert=False,forec_update=False,commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        extention = image_url.rsplit('.',1)[1].lower()
        image_name = f'{name}.{extention}'

        respnse = request.urlopen(image_url)
        image.image.save(image_name,ContentFile(respnse.read()),save=False)

        if commit:
            image.save()
        return image
