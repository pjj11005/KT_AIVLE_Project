# forms.py
from django import forms

class UploadFileForm(forms.Form):
    csv_file = forms.FileField()
