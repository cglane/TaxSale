# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from django.contrib import admin
from properties.models import (Property, CensusTract)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('address', 'status','percent_black' )
    readonly_fields = ('percent_black', 'percent_white' )
    search_fields = ['property_pin', 'address']
    def percent_black(self, instance):
        if instance.census_tract:
            return instance.census_tract.percent_black
        return 'Unavailable'
    def percent_white(self, instance):
        return instance.census_tract.percent_white

    list_filter = ('status', 'property_class_code')

@admin.register(CensusTract)
class CensusAdmin(admin.ModelAdmin):
    pass

