# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import (Property, CensusTract)
from django.http import HttpResponse
from django.shortcuts import render
from forms import (SimpleForm, )
# Create your views here.

def landing_form(request):
    if request.method == "POST":
        form = SimpleForm(request.POST)
        if form.is_valid():
            img_name = 'data-maps/test.jpg'
            print img_name, 'name'
            return render(request, 'properties/post_edit.html', {'form': form, 'img': img_name})
    else:
        form = SimpleForm()
    return render(request, 'properties/post_edit.html', {'form': form})