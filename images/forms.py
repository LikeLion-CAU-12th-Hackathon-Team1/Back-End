from django import forms

class FolderUploadForm(forms.Form):
    folder_path = forms.CharField(max_length=255)