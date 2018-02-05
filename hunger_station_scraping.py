#!/usr/bin/env python

import logging
import os
from grab import Grab
import csv
import re

logging.basicConfig(level=logging.DEBUG)
HUNGER_STATION = 'https://hungerstation.com/'
g = Grab()
g.go(HUNGER_STATION)

class Restaurant:
    def __init__(self, name, area):
        self.name = name   
        self.areas = [area] 

    def add_area(self, area):
        self.areas.append(area)

class Area:
    def __init__(self, name, delivery_fee):
        self.name = name   
        self.delivery_fee = delivery_fee


def get_areas_ref_and_names():
    try:
        # RIYADH
        g.go('en/riyadh')
        areas_refs = g.doc.select("//*[@id='district-sec']/div/div/ul//@href")
    except Exception as e:
        print(type(e))
        print(e)
    areas_refs = areas_refs.node_list()
    areas_names = [i.split('/')[3] for i in areas_refs]
    return areas_refs, areas_names

def get_all_restaurants_in_area():
    try:
        restaurants_in_area = g.doc.select("//*[@id='mainc']/div[2]/div//div[@data-name]")
    except Exception as e:
        print(type(e))
        print(e)
    return restaurants_in_area

def add_all_restaurants_data(restaurants, restaurants_divs, area_name):
    for div in restaurants_divs:
        delivery_fee_xpath = div.xpath("a/div[@class='smallvalue'][2]/p[2]/text()")
        delivery_fee_regex = re.search('^\D*(\d+(?:\.?\d+)?)', delivery_fee_xpath[0])
        if delivery_fee_regex is not None:
            delivery_fee = float(delivery_fee_regex.group(1))
        else:
            delivery_fee = 0.0
        
        restaurant_name_xpath = div.xpath("a/@href")
        restaurant_name = restaurant_name_xpath[0].split('/')[-1]

        was_already_added = False
        for i in restaurants:
            if i.name == restaurant_name:
                was_already_added = True
                restaurant = i
                break
        
        if was_already_added:
            area = Area(area_name,delivery_fee)
            restaurant.add_area(area)
        else:
            restaurants.append(Restaurant(restaurant_name,Area(area_name,delivery_fee)))

def generate_restaurant_dicts(restaurants):
    dict_data = []
    for r in restaurants:
        restaurant_dict = {}
        restaurant_dict['restaurant_instance'] = r.name
        for area in r.areas:
            restaurant_dict[area.name] = area.delivery_fee
        
        dict_data.append(restaurant_dict)
    return dict_data

def write_dict_to_csv(csv_file, csv_columns, dict_data):
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in dict_data:
                writer.writerow(data)
    except IOError as err:
        errno, strerror = err.args
        print("I/O error({0}): {1}".format(errno, strerror))  
    return            

def main():  
    areas_ref, area_names = get_areas_ref_and_names()
    areas = list(zip(areas_ref, area_names))
    csv_columns = ['restaurant_instance']
    restaurants = []

    for area in areas:
        csv_columns.append(area[1])
    for ref, area_name in areas:
        g.go(ref)
        restaurants_divs = get_all_restaurants_in_area().node_list()
        add_all_restaurants_data(restaurants, restaurants_divs, area_name)

    dict_data = generate_restaurant_dicts(restaurants)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    csv_file = os.path.join(dir_path,'riyadh_delivery_fees.csv')
    
    write_dict_to_csv(csv_file, csv_columns, dict_data)

if __name__ == "__main__":
    main()