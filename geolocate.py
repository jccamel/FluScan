#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# Uso de la API maxmind
# https://dev.maxmind.com/geoip/geoip2/web-services/#IP_Geolocation_Usage

import pygeoip
import geoip2.webservice


class GeoLocate(object):
    """
    GeoIP2 Precision Services
    Insights - Insights service provides our most accurate information about the location of an IP address,
        pinpointing it to the zip or postal code level. It includes confidence factors for geolocation data,
        describes the ISP/Organization, and indicates the type of user behind the IP.
    City - City service provides our most accurate information about the location of an IP address
        to the zip or postal code level and identifies the associated ISP or organization.
    Country - Country service is best for customers who only need to know the country of an IP address.
    db - Hard disk Database request
    """
    def __init__(self, ip, select):
        self.ip = ip
        self.sel = select
        self.response = ''
        self.dicc = {}
        self.query_remain = 0

    def __del__(self):
        pass

    def __country(self):
        # A two-character code for the continent associated with the IP address. The possible codes are:
        # AF - Africa; AN - Antarctica; AS - Asia; EU - Europe
        # NA - North America; OC - Oceania; SA - South America
        self.dicc['continent_code'] = self.response.continent.code
        # A unique identifier for the continent as specified by GeoNames.
        self.dicc['continent_id'] = self.response.continent.geoname_id
        # A map from locale codes, such as en, to the localized names for the feature.
        self.dicc['continent_name'] = self.response.continent.names['en']
        # ----------------------------------------------------------------------------------
        # A two-character ISO 3166-1 country code for the country associated with the IP address.
        self.dicc['country_iso_code'] = self.response.country.iso_code
        # A unique identifier for the country as specified by GeoNames.
        self.dicc['country_id'] = self.response.country.geoname_id
        # A map from locale codes, such as en, to the localized names for the feature.
        self.dicc['country'] = self.response.country.names['en']
        # ----------------------------------------------------------------------------------
        # The requested IP address.
        self.dicc['ip_address'] = self.response.traits.ip_address
        # ***Deprecated***. Please see our GeoIP2 Anonymous IP database to determine whether the
        # IP address is used by an anonymizing service. (boolean)
        self.dicc['is_anonymous_proxy'] = str(self.response.traits.is_anonymous_proxy)
        self.query_remain = self.response.maxmind.queries_remaining

    def __city(self):
        self.__country()
        # A map from locale codes, such as en, to the localized names for the feature.
        self.dicc['city'] = self.response.city.names['en']
        # http://www.geonames.org/geoname_id/city.html
        self.dicc['city_id'] = self.response.city.geoname_id
        # ----------------------------------------------------------------------------------
        # The approximate accuracy radius in kilometers around the latitude and longitude
        # for the IP address. This is the radius where we have a 67% confidence that the device
        # using the IP address resides within the circle centered at the latitude and longitude
        # with the provided radius.
        self.dicc['accuracy_radius'] = self.response.location.accuracy_radius
        # The approximate latitude of the location associated with the IP address.
        # This value is not precise and should not be used to identify a particular address or household
        self.dicc['latitude'] = self.response.location.latitude
        # The approximate longitude of the location associated with the IP address.
        # Latitude and Longitude are often near the center of population.
        # These values are not precise and should not be used to identify a particular address or household.
        self.dicc['longitude'] = self.response.location.longitude
        # The time zone associated with location, as specified by the
        # IANA Time Zone Database, e.g., “America/New_York”.
        self.dicc['time_zone'] = self.response.location.time_zone
        # ----------------------------------------------------------------------------------
        # The name of the ISP associated with the IP address.
        self.dicc['isp'] = self.response.traits.isp
        # The name of the organization associated with the IP address.
        self.dicc['organization'] = self.response.traits.organization
        # The autonomous system number associated with the IP address.
        self.dicc['autonomous_system_number'] = self.response.traits.autonomous_system_number
        # The organization associated with the registered autonomous system number for the IP address.
        self.dicc['autonomous_system_organization'] = self.response.traits.autonomous_system_organization

    def __insights(self):
        # A value from 0-100 representing our confidence that the country is correct.
        self.dicc['country_confidence'] = self.response.country.confidence
        # ----------------------------------------------------------------------------------
        # A value from 0-100 representing our confidence that the city is correct.
        self.dicc['city_confidence'] = self.response.city.confidence
        # ----------------------------------------------------------------------------------
        # The user type associated with the IP address. This will be one of the following values.
        # business, cafe, cellular, college, content_delivery_network, dialup, government, hosting, library
        # military, residential, router, school, search_engine_spider, traveler
        self.dicc['user_type'] = self.response.traits.user_type

    def __dataquery(self):

        if self.sel != 'db':
            client = geoip2.webservice.Client({USER}, {KEY}) # User and Key MAXMIND Acount
            if self.sel == 'insights':
                self.response = client.insights(self.ip)
                self.__country()
                self.__city()
                self.__insights()
                print "Remain insight queries: %s\n" % str(self.query_remain)
            elif self.sel == 'city':
                self.response = client.city(self.ip)
                self.__city()
                self.__country()
                print "Remain city queries: %s\n" % str(self.query_remain)
            elif self.sel == 'country':
                self.response = client.country(self.ip)
                self.__country()
                print "Remain country queries: %s\n" % str(self.query_remain)
        elif self.sel == "db":
            try:
                geoDb = pygeoip.GeoIP('GeoIP/GeoLiteCity.dat')
                ip_dictionary_values = geoDb.record_by_addr(self.ip)
                for value in ip_dictionary_values.items():
                    self.dicc[value[0]] = str(value[1])
            except:
                print "error"
        else:
            pass

    def geolocate_doc(self):
        self.__dataquery()
        return self.dicc
