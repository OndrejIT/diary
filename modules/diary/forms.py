# Author Ondrej Barta
# ondrej@ondrej.it
# Copyright 2017-2018

from django import forms

from .models import Collection, Item


class CollectionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CollectionForm, self).__init__(*args, **kwargs)
        self.fields["token"].widget.attrs["style"] = "width:350px;"
        self.fields["name"].widget.attrs["style"] = "width:350px;"

    class Meta(object):
        fields = ("name",)
        model = Collection
        widgets = {
            "name": forms.TextInput,
        }


class ItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs["style"] = "width:600px;"

    class Meta(object):
        fields = ("name",)
        model = Item
        widgets = {
            "name": forms.TextInput,
        }
