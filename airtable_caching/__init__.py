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
Author: Ross Mountjoy (https://github.com/rmountjoy92)
Contributors: 
Thomas Huxley (https://github.com/bawpcwpn)                                     
"""


class Base:
    def __init__(self, base_id, api_key, json_folder=None):
        """
        The base class is responsible for caching tables and clearing the cache.

        :param base_id: (str) The base key found in the API documentation
        for the base in Airtable.

        :param api_key: (str) Your Airtable user's API Key from
        your account page in Airtable.

        :param json_folder: (path) Path location for caching the .json files.
        """

        self.base_id = base_id
        self.api_key = api_key

        # get json folder path
        if json_folder is None:
            curr_folder = os.path.dirname(__file__)
            main_json_folder = os.path.join(curr_folder, "json")
        else:
            main_json_folder = os.path.abspath(json_folder)
        if not os.path.isdir(main_json_folder):
            os.mkdir(main_json_folder)
        self.json_folder = os.path.join(main_json_folder, self.base_id)
        if not os.path.isdir(self.json_folder):
            os.mkdir(self.json_folder)

    def cache_table(self, table_name, **kwargs):
        """
        Save table using airtable-python-wrapper's get_all function as a json file.

        :param table_name: (str) The name of the table to cache, case-sensitive.

        :param kwargs: (kwargs) Keyword arguments to pass to the get_all function, see
        https://airtable-python-wrapper.readthedocs.io/en/master/api.html#airtable.Airtable.get_all

        :return None:
        """

        airtable = Airtable(self.base_id, table_name, self.api_key)
        at_json = {"list": airtable.get_all(**kwargs)}
        json_path = os.path.join(self.json_folder, f"{table_name}.json")
        with open(json_path, "w") as new_file:
            json.dump(at_json, new_file)

    def clear_cache(self):
        """
        Delete all json files out of this base's json folder.

        :return None:
        """
        rmtree(self.json_folder)
        os.mkdir(self.json_folder)


class Table:
    def __init__(self, base_id, table_name, json_folder=None):
        """
        The table class is what you use to query the cached data.

        :param base_id: (str) The base key found in the API documentation
        for the base in Airtable.

        :param table_name: (str) The name of the table to access, case-sensitive.

        :param json_folder: (path) Path location for caching the .json files.
        """

        self.base_id = base_id
        self.table_name = table_name
        self.list = None

        # get json folder path
        if json_folder is None:
            curr_folder = os.path.dirname(__file__)
            main_json_folder = os.path.join(curr_folder, "json")
        else:
            main_json_folder = os.path.abspath(json_folder)
        self.json_folder = os.path.join(main_json_folder, self.base_id)

    def get(self, rec_id, resolve_fields=None):
        """
        Get the data for the given record ID from cached .json as a dict.
        Optionally resolve linked records.

        :param rec_id: (str) The Airtable record ID for the record to access

        :param resolve_fields: (dict) The linked records fields to resolve,
        using {<Table Name>: <Linked Field Name>}

        :return dict:
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
        Get the data for all records from cached .json
        Optionally resolve linked records.
        Then sets self.list as a list of dicts.

        :param resolve_fields: (dict) The linked records fields to resolve,
        using {<Table Name>: <Linked Field Name>}

        :return self: Table Class Object
        """

        self.__get_dict_list_from_json_file()
        if resolve_fields:
            self.__resolve_relationships(resolve_fields)
        if len(self.list) < 1:
            self.list = None
        return self

    def filter_by(self, fields):
        """
        Filters self.list by field/value pairs.

        :param fields: (dict) field/value pairs in which to filter self.list,
        using {<field>:<value>}

        :return self: Table Class Object
        """

        for field, value in fields.items():
            self.list = [rec for rec in self.list if rec["fields"].get(field) == value]
        if len(self.list) < 1:
            self.list = None
        return self

    def order_by(self, field, desc=False):
        """
        Orders self.list by the given field.

        :param field: (str) The field name to sort by.

        :param desc: (bool) If True, orders self.list descending.

        :return self: Table Class Object
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
        Returns all of self.list

        :return list:
        """
        return self.list

    def first(self):
        """
        Returns the first record in self.list

        :return dict:
        """
        if len(self.list) < 1:
            return None
        return self.list[0]

    def last(self):
        """
        Returns the last record in self.list

        :return dict:
        """
        if len(self.list) < 1:
            return None
        return self.list[-1]

    def __get_dict_list_from_json_file(self):
        """
        Private method that converts the configured .json into a list of dicts
        :return None:
        """
        while True:
            try:
                with open(
                    os.path.join(self.json_folder, f"{self.table_name}.json"), "r"
                ) as json_file:
                    table_dict = json.load(json_file)
                self.list = table_dict["list"]
                break
            except json.decoder.JSONDecodeError:
                print("Attempted to read and cache at the same time, trying again.")
                continue

    def __resolve_relationships(self, resolve_fields):
        """
        Private method that replaces linked record ID's with the full record.

        :param resolve_fields: (dict) The linked records fields to resolve,
        using {<Table Name>: <Linked Field Name>}

        :return None:
        """
        for table_name, rel_field in resolve_fields.items():
            for rec in self.list:
                full_rec_list = []
                if rec["fields"].get(rel_field, None):
                    for related_rec in rec["fields"][rel_field]:
                        d = Table(base_id=self.base_id, table_name=table_name)
                        full_rec_list.append(d.get(related_rec))
                    rec["fields"][rel_field] = full_rec_list
