# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# Create your models here.
class CensusTract(models.Model):
  year = models.CharField(max_length=5)
  tract_number = models.IntegerField()
  black_total = models.IntegerField()
  white_total = models.IntegerField()
  population_total = models.IntegerField()
  county = models.IntegerField()
  state = models.IntegerField()
  @classmethod
  def create(self, response, census_map, data_year):
      """Parse the response and then create a workable object for
        saving the tract object
      """
      response_val = response.json()
      res_dict = dict(zip(response_val[0], response_val[1]))
      model_dict = {census_map[name]: val for name, val in res_dict.iteritems()}
      model_dict['year'] = data_year
      tract = self(**model_dict)
      tract.save()
      return tract
class Property(models.Model):
  """A Property that is going up for auction including whether the property was
    Deeded or Not.
  """
  year = models.IntegerField()
  address = models.CharField(max_length=50)
  property_pin = models.IntegerField()
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

