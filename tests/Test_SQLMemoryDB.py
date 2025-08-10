#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
import unittest

import peewee

from clickpoints.includes.Database import SQLMemoryDBFromFile


class Test_SQLMemoryDB(unittest.TestCase):

    def test_shared_memory_db_across_threads(self):
        fd, filename = None, "shared_test.db"
        try:
            db = peewee.SqliteDatabase(filename)

            class BaseModel(peewee.Model):
                class Meta:
                    database = db

            class Image(BaseModel):
                name = peewee.CharField()

            db.connect()
            db.create_tables([Image])
            Image.create(name="foo")
            db.close()

            mem_db = SQLMemoryDBFromFile(filename)

            cur = mem_db.execute_sql("SELECT name FROM image")
            self.assertEqual(cur.fetchone()[0], "foo")

            result = []

            def worker():
                cur = mem_db.execute_sql("SELECT name FROM image")
                result.append(cur.fetchone()[0])

            t = threading.Thread(target=worker)
            t.start()
            t.join()

            self.assertEqual(result, ["foo"])
            mem_db.close()
        finally:
            if os.path.exists(filename):
                os.remove(filename)


if __name__ == "__main__":
    unittest.main()

