import os
import unittest
from pathlib import Path
from shutil import rmtree
from airtable_caching import Base, Table


class Tests(unittest.TestCase):
    def setUp(self):
        # standard set up, makes json folder automatically
        self.base = Base(base_id="appjMwyFviPaM9I0L", api_key="keyqhxncgPbSySJQN")

        # custom json folder set up, user supplies json folder
        self.custom_json_folder = os.path.join(os.path.dirname(__file__), "custom_json")
        self.base_with_custom_json_folder = Base(
            base_id="appjMwyFviPaM9I0L",
            api_key="keyqhxncgPbSySJQN",
            json_folder=self.custom_json_folder,
        )

        # cache some tables
        self.base.cache_table("Table 1")
        self.base.cache_table("Table 2")
        self.base_with_custom_json_folder.cache_table("Table 1")
        self.base_with_custom_json_folder.cache_table("Table 2")

        # init a table class (w/o custom json folder)
        self.table1 = Table(base_id="appjMwyFviPaM9I0L", table_name="Table 1")

        # init a table class (w/ custom json folder)
        self.table1_with_custom_json_folder = Table(
            base_id="appjMwyFviPaM9I0L",
            table_name="Table 1",
            json_folder=self.custom_json_folder,
        )

    def tearDown(self):
        # remove json folders
        rmtree(Path(self.base.json_folder).parent)
        rmtree(Path(self.base_with_custom_json_folder.json_folder).parent)

    def test_cache_table(self):
        # test to make sure tables are cached correctly
        self.assertTrue(
            os.path.isfile(os.path.join(self.base.json_folder, "Table 1.json"))
        )
        self.assertTrue(
            os.path.isfile(os.path.join(self.base.json_folder, "Table 2.json"))
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    self.base_with_custom_json_folder.json_folder, "Table 1.json"
                )
            )
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(
                    self.base_with_custom_json_folder.json_folder, "Table 2.json"
                )
            )
        )

    def test_get(self):
        # testing the table.get method using base 1 table 1 rec 1
        rec = self.table1.get("rec4trz5QrB6aWJBw")
        self.assertTrue(
            rec["fields"]["Name"] == "Data entry 1 from Table 1 from Base 1"
        )

        # from custom json folder
        rec = self.table1_with_custom_json_folder.get("rec4trz5QrB6aWJBw")
        self.assertTrue(
            rec["fields"]["Name"] == "Data entry 1 from Table 1 from Base 1"
        )

    def test_query(self):
        # without resolving relationships
        query = self.table1.query().list
        self.assertTrue(isinstance(query, list))
        self.assertTrue(len(query) == 3)
        self.assertTrue(isinstance(query[0]["fields"]["Link to Table 2"][0], str))

        # test resolving relationships
        query = self.table1.query(resolve_fields={"Table 2": "Link to Table 2"}).list
        self.assertTrue(
            query[0]["fields"]["Link to Table 2"][0].get("fields") is not None
        )

    def test_filter_by(self):
        query = (
            self.table1.query()
            .filter_by({"Name": "Data entry 1 from Table 1 from Base 1"})
            .list
        )
        self.assertTrue(len(query) == 1)

    def test_order_by(self):
        query = self.table1.query().order_by("Number").list
        self.assertTrue(query[0]["fields"]["Number"] == 1)

        query = self.table1.query().order_by("Number", desc=True).list
        self.assertTrue(query[0]["fields"]["Number"] == 3)

    def test_all(self):
        query = self.table1.query()
        self.assertTrue(query.list == query.all())

    def test_first(self):
        query = self.table1.query()
        self.assertTrue(query.list[0] == query.first())

    def test_last(self):
        query = self.table1.query()
        self.assertTrue(query.list[-1] == query.last())
