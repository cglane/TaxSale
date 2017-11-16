# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class CensusTract(models.Model):
  year = models.PositiveSmallIntegerField()
  number = models.IntegerField()
  percent_white = models.DecimalField(max_digits=4,decimal_places=2)
  percent_black = models.DecimalField(max_digits=4,decimal_places=2)
  percent_hispanic = models.DecimalField(max_digits=4,decimal_places=2)
  occupied_housing = models.DecimalField(max_digits=4,decimal_places=2)

class Property(models.Model):
  """A Property that is going up for auction including whether the property was
    Deeded or Not.
  """
  year = models.IntegerField()
  address = models.CharField(max_length=50)
  tract = models.IntegerField()
  zip_code = models.CharField(max_length=10)
  tax_debt = models.FloatField()
  property_value = models.IntegerField()
  property_class_code = models.CharField(max_length=50)
  owner_address = models.CharField(max_length=50)
  lat = models.FloatField()
  lng = models.FloatField()
  min_bid = models.DecimalField(max_digits=20,decimal_places=2)
  status = models.BooleanField()
  highest_sales_price = models.DecimalField(max_digits=20,decimal_places=2)
  finished_sq_feet = models.PositiveSmallIntegerField()
  acreage = models.DecimalField(max_digits=10,decimal_places=2)
  bedrooms = models.PositiveSmallIntegerField()
  constructed_year = models.PositiveSmallIntegerField()
  census_tract = models.ForeignKey(CensusTract, on_delete = models.CASCADE)

  def __str__(self):
    return self.address

