# -*- coding: utf-8 -*-
"""Test for checking if the response format is proper. Run test_crud before running this"""

import unittest
import tempfile
import os
import hydrus.app as views
import json
from hydrus.app import API_NAME, SERVER_URL



class ViewsTestCase(unittest.TestCase):
    """Test Class for the app."""

    def setUp(self):
        """Temporary database setup to store responses."""
        self.db_fd, views.app.config['DATABASE'] = tempfile.mkstemp()
        views.app.config['TESTING'] = True
        self.app = views.app.test_client()

    def tearDown(self):
        """Tear down temporary database."""
        os.close(self.db_fd)
        os.unlink(views.app.config['DATABASE'])

    def test_Index(self):
        """Test for the index."""
        response_get = self.app.get("/"+API_NAME)
        self.endpoints = json.loads(response_get.data.decode('utf-8'))
        response_post = self.app.post("/"+API_NAME, data={})
        response_delete = self.app.delete("/"+API_NAME)
        assert "@context" in self.endpoints
        assert self.endpoints["@id"] == "/"+API_NAME
        assert self.endpoints["@type"] == "EntryPoint"
        assert response_get.status_code == 200
        assert response_post.status_code == 405
        assert response_delete.status_code == 405

    def test_EntryPoint_context(self):
        """Test for the EntryPoint context."""
        response_get = self.app.get("/"+API_NAME +"/contexts/EntryPoint.jsonld")
        response_get_data = json.loads(response_get.data.decode('utf-8'))
        response_post = self.app.post("/"+API_NAME +"/contexts/EntryPoint.jsonld", data={})
        response_delete = self.app.delete("/"+API_NAME +"/contexts/EntryPoint.jsonld")
        assert response_get.status_code == 200
        assert "@context" in response_get_data
        assert response_post.status_code == 405
        assert response_delete.status_code == 405

    def test_Vocab(self):
        """Test the vocab."""
        response_get = self.app.get("/"+API_NAME +"/vocab#")
        response_get_data = json.loads(response_get.data.decode('utf-8'))
        assert "@context" in response_get_data
        # print(response_get_data["@id"], SERVER_URL+API_NAME +"/vocab#")
        assert response_get_data["@type"] == "ApiDocumentation"
        assert response_get_data["@id"] == SERVER_URL+API_NAME +"/vocab"
        assert response_get.status_code == 200

        response_delete = self.app.delete("/"+API_NAME +"/vocab#")
        assert response_delete.status_code == 405

        response_put = self.app.put("/"+API_NAME +"/vocab#", data=json.dumps(dict(foo = 'bar')))
        assert response_put.status_code == 405

    def test_Endpoints_Collections(self):
        """Test all endpoints to get the collection."""
        index = self.app.get("/"+API_NAME)
        assert index.status_code == 200
        endpoints = json.loads(index.data.decode('utf-8'))
        for endpoint in endpoints:
            if endpoint not in ["@id", "@context", "@type"] and "Collection" in endpoints[endpoint]:
                response_get = self.app.get(endpoints[endpoint])
                response_post = self.app.post(endpoints[endpoint], data=json.dumps(dict(foo = 'bar')))
                response_delete = self.app.delete(endpoints[endpoint])
                assert response_get.status_code == 200
                assert response_post.status_code == 201
                assert response_delete.status_code == 405
                response_get_data = json.loads(response_get.data.decode('utf-8'))
                assert "@context" in response_get_data
                assert "@id" in response_get_data
                assert "@type" in response_get_data
                assert "members" in response_get_data

    def test_Endpoints_Contexts(self):
        """Test all endpoints contexts are generated properly."""
        index = self.app.get("/"+API_NAME)
        assert index.status_code == 200
        endpoints = json.loads(index.data.decode('utf-8'))
        for endpoint in endpoints:
            if endpoint not in ["@id", "@context", "@type"] and "Collection" in endpoints[endpoint]:
                response_get = self.app.get(endpoints[endpoint])
                # print(response_get.data.decode('utf-8'))
                context = json.loads(response_get.data.decode('utf-8'))["@context"]
                response_context = self.app.get(context)
                response_context_data = json.loads(response_context.data.decode('utf-8'))
                assert response_context.status_code == 200
                assert "@context" in response_context_data


if __name__ == '__main__':
    message = """
    Running tests for the app. Checking if all responses are in proper order.
    NOTE: This doesn't ensure that data is entered or deleted in a proper manner.
    It only checks the format of the reponses.
    If you want to check data entry, please run test_crud.py
    """
    print(message)
    unittest.main()
