import os
import json
from shutil import rmtree
from airtable import Airtable

"""
 █████╗ ██╗██████╗ ████████╗ █████╗ ██████╗ ██╗     ███████╗
██╔══██╗██║██╔══██╗╚══██╔══╝██╔══██╗██╔══██╗██║     ██╔════╝
███████║██║██████╔╝   ██║   ███████║██████╔╝██║     █████╗  
██╔══██║██║██╔══██╗   ██║   ██╔══██║██╔══██╗██║     ██╔══╝  
██║  ██║██║██║  ██║   ██║   ██║  ██║██████╔╝███████╗███████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚══════╝╚══════╝

 ██████╗ █████╗  ██████╗██╗  ██╗██╗███╗   ██╗ ██████╗ 
██╔════╝██╔══██╗██╔════╝██║  ██║██║████╗  ██║██╔════╝ 
██║     ███████║██║     ███████║██║██╔██╗ ██║██║  ███╗
██║     ██╔══██║██║     ██╔══██║██║██║╚██╗██║██║   ██║
╚██████╗██║  ██║╚██████╗██║  ██║██║██║ ╚████║╚██████╔╝
 ╚═════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
Author: Ross Mountjoy                                             
"""


class Base:
    def __init__(self, name, key, api_key):
        self.name = name
        self.key = key
        self.api_key = api_key

        # get json folder path
        curr_folder = os.path.dirname(__file__)
        main_json_folder = os.path.join(curr_folder, "json")
        if not os.path.isdir(main_json_folder):
            os.mkdir(main_json_folder)
        self.json_folder = os.path.join(main_json_folder, self.name)
        if not os.path.isdir(self.json_folder):
            os.mkdir(self.json_folder)

    def cache_table(self, table_name, **kwargs):
        """
        save table using airtable-python-wrapper's get_all function as a json file
        :param table_name:
        :param kwargs:
        :return:
        """
        airtable = Airtable(self.key, table_name, self.api_key)
        at_json = {"list": airtable.get_all(**kwargs)}
        json_path = os.path.join(self.json_folder, f"{table_name}.json")
        if os.path.isfile(json_path):
            os.remove(json_path)
        with open(json_path, "w") as new_file:
            json.dump(at_json, new_file)

    def clear_cache(self):
        """
        delete all json files out of this base's json folder
        :return:
        """
        rmtree(self.json_folder)
        os.mkdir(self.json_folder)


class Table:
    def __init__(self, base, table_name):
        self.base = base
        self.table_name = table_name
        self.list = None

        # get json folder path
        curr_folder = os.path.dirname(__file__)
        self.json_folder = os.path.join(curr_folder, "json")

    def get(self, rec_id, resolve_fields=None):
        """
        reads json file for given record id, optionally resolves relationships,
        then returns the record as a dict
        :param rec_id:
        :param resolve_fields:
        :return:
        """
        self.__get_dict_list_from_json_file()
        if resolve_fields:
            self.__resolve_relationships(resolve_fields)
        recs = [rec for rec in self.list if rec["id"] == rec_id]
        if not recs:
            return None
        return recs[0]

    def query(self, resolve_fields=None):
        """
        reads json file for all records, optionally resolves relationships,
        then sets self.list as a list of dicts.
        :param resolve_fields:
        :return:
        """
        self.__get_dict_list_from_json_file()
        if resolve_fields:
            self.__resolve_relationships(resolve_fields)
        if len(self.list) < 1:
            self.list = None
        return self

    def filter_by(self, fields):
        """
        filters self.list by a given dict of {<field>:<value>}
        :param fields:
        :return:
        """
        for field, value in fields.items():
            self.list = [rec for rec in self.list if rec["fields"].get(field) == value]
        if len(self.list) < 1:
            self.list = None
        return self

    def order_by(self, field, desc=False):
        """
        orders self.list by the given field, set desc to order descending
        :param field:
        :param desc:
        :return:
        """
        try:
            self.list = sorted(self.list, key=lambda i: i["fields"].get(field, None))
        except TypeError:
            raise Exception(
                f"Invalid field error: '{field}' does not exist in {self.table_name}'s ['fields'] dict."
            )

        if len(self.list) < 1:
            self.list = None
        if desc and self.list:
            self.list.reverse()
        return self

    def all(self):
        """
        returns all of self.list
        :return:
        """
        return self.list

    def first(self):
        """
        returns the first record in self.list
        :return:
        """
        if len(self.list) < 1:
            return None
        return self.list[0]

    def last(self):
        """
        returns the last record in self.list
        :return:
        """
        if len(self.list) < 1:
            return None
        return self.list[-1]

    def __get_dict_list_from_json_file(self):
        with open(
            os.path.join(self.base.json_folder, f"{self.table_name}.json"), "r"
        ) as json_file:
            table_dict = json.load(json_file)
        self.list = table_dict["list"]

    def __resolve_relationships(self, resolve_fields):
        for table_name, rel_field in resolve_fields.items():
            for rec in self.list:
                full_rec_list = []
                if rec["fields"].get(rel_field, None):
                    for related_rec in rec["fields"][rel_field]:
                        d = Table(base=self.base, table_name=self.table_name)
                        full_rec_list.append(d.get(related_rec))
                    rec["fields"][rel_field] = full_rec_list
