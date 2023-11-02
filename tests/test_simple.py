from argparse import Namespace
import pytest
from bifrostlib import common
from bifrostlib import datahandling
from bifrostlib import database_interface
from bifrostlib.datahandling import ComponentReference
from bifrostlib.datahandling import Component
from bifrostlib.datahandling import SampleReference
from bifrostlib.datahandling import Sample
from bifrostlib.datahandling import RunReference
from bifrostlib.datahandling import Run
from bifrost_cge_mlst import launcher
import pymongo
import os
import shutil


@pytest.fixture
def test_connection():
    assert datahandling.has_a_database_connection()
    assert "TEST" in os.environ['BIFROST_DB_KEY'].upper()  # A very basic piece of protection ensuring the word test is in the DB

def test_cwd():
    bifrost_install_dir = os.environ['BIFROST_INSTALL_DIR']
    print(f'bifrost cwd: {bifrost_install_dir}')
    assert bifrost_install_dir != ''

class TestCGEmlst:
    component_name = "cge_mlst__v2.2.10"
    component_name = component_name + "__5e385d4"

    bifrost_install_dir = os.environ['BIFROST_INSTALL_DIR']
    
    test_dir = f"{bifrost_install_dir}/bifrost/test_data/output/test__cge_mlst"
    r1 = f"{bifrost_install_dir}/bifrost/test_data/samples/S1_R1.fastq.gz"
    r2 = f"{bifrost_install_dir}/bifrost/test_data/samples/S1_R2.fastq.gz"
    json_entries = [
        {
            "_id": {"$oid": "000000000000000000000001"},
            "name": "S1",
            "components": [],
            "categories": {
                "paired_reads": {
                    "summary": {
                        "data": [r1,
                                 r2]
                    }
                },
                "species_detection": {
                    "summary": {
                        "species": "Staphylococcus aureus"
                    }
                }
            }
        }
    ]
    bson_entries = [database_interface.json_to_bson(i) for i in json_entries]

    @classmethod
    def setup_class(cls):
        client = pymongo.MongoClient(os.environ['BIFROST_DB_KEY'])
        db = client.get_database()
        cls.clear_all_collections(db)
        col = db["samples"]
        col.insert_many(cls.bson_entries)
        launcher.initialize()
        os.chdir(cls.bifrost_install_dir)

    @classmethod
    def teardown_class(cls):
        client = pymongo.MongoClient(os.environ['BIFROST_DB_KEY'])
        db = client.get_database()
        cls.clear_all_collections(db)

    @staticmethod
    def clear_all_collections(db):
        db.drop_collection("components")
        db.drop_collection("hosts")
        db.drop_collection("run_components")
        db.drop_collection("runs")
        db.drop_collection("sample_components")
        db.drop_collection("samples")

    def test_info(self):
        launcher.run_pipeline(["--info"])

    def test_help(self):
        launcher.run_pipeline(["--help"])

    def test_pipeline(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir)

        os.makedirs(self.test_dir)
        test_args = [
            "--sample_name", "S1",
            "--outdir", self.test_dir
        ]
        launcher.main(args=test_args)
        assert os.path.exists(f"{self.test_dir}/{self.component_name}/datadump_complete") == True
        shutil.rmtree(self.test_dir)
        assert not os.path.isdir(f"{self.test_dir}/{self.component_name}")

    def test_db_output(self):
        with pymongo.MongoClient(os.environ['BIFROST_DB_KEY']) as client:
            print(f'databases: {client.list_database_names()}')
            db = client.get_database()
            print(f'collections: {db.list_collection_names()}')
            sample = db['samples']
            sample_data = sample.find_one({})
            print(f'sample_data: {sample_data}')
            
            assert len(sample_data) > 1
            assert sample_data['categories']['mlst']['summary']['sequence_type']['saureus'] == '5?*'
