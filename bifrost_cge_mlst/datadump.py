from bifrostlib import common
from bifrostlib.datahandling import Sample
from bifrostlib.datahandling import SampleComponentReference
from bifrostlib.datahandling import SampleComponent
from bifrostlib.datahandling import Component
from bifrostlib.datahandling import Category
from typing import Dict
import os
import re
from git import Repo

def extract_mlst(mlst: Category, results: Dict, component_name: str, species) -> None:
    file_name = "data.yaml"
    file_key = common.json_key_cleaner(file_name)
    file_path = os.path.join(component_name, file_name)
    mlst_yaml = common.get_yaml(file_path)
    results[file_key] = {}
    for subspec in species:
        mlst_results = mlst_yaml[subspec]['mlst']['results']
        mlst_run_info = mlst_yaml[subspec]['mlst']['run_info']
        mlst_user_input = mlst_yaml[subspec]['mlst']['user_input']
        sequence_type = mlst_results['sequence_type']
        mlst['summary']['sequence_type'][subspec]=sequence_type
        loci = mlst_results['allele_profile'].keys()
        allele_dict = {locus:mlst_results['allele_profile'][locus]['allele'] for locus in loci}
        mlst['report']['data'].append({
            "db":subspec,
            "sequence_type":sequence_type,
            "alleles":allele_dict
        })
    results[file_key]['sequence_type'] = mlst['summary']['sequence_type']

def datadump(samplecomponent_ref_json: Dict):
    samplecomponent_ref = SampleComponentReference(value=samplecomponent_ref_json)
    samplecomponent = SampleComponent.load(samplecomponent_ref)
    sample = Sample.load(samplecomponent.sample)
    component = Component.load(samplecomponent.component)
    database_path = f"{os.environ['BIFROST_INSTALL_DIR']}/bifrost/components/bifrost_{component['display_name']}/{component['resources']['database_path']}" 
    species_detection = sample.get_category("species_detection")
    species = species_detection["summary"].get("species", None)
    mlst_species = component["options"]["mlst_species_mapping"][species]
    db_repo = Repo(database_path)
    db_commit = str(db_repo.head.commit)
    mlst = samplecomponent.get_category("mlst")
    #if mlst is None: # remove this line
    mlst = Category(value={
            "name": "mlst",
            "component": {"id": samplecomponent["component"]["_id"], "name": samplecomponent["component"]["name"]},
            "summary": {"sequence_type":{}},
            "report": {"data":[]}
        }
    )
    extract_mlst(mlst, samplecomponent["results"], samplecomponent["component"]["name"], mlst_species)
    mlst['database_versions'] = {'mlst_db':db_commit}
    samplecomponent.set_category(mlst)
    sample_category = sample.get_category("mlst")
    if sample_category == None:
        sample.set_category(mlst)
    else:
        current_category_version = extract_digits_from_component_version(mlst['component']['name'])
        sample_category_version = extract_digits_from_component_version(sample_category['component']['name'])
        print(current_category_version, sample_category_version)
        if current_category_version >= sample_category_version:
            sample.set_category(mlst)
    common.set_status_and_save(sample, samplecomponent, "Success")
    
    with open(os.path.join(samplecomponent["component"]["name"], "datadump_complete"), "w+") as fh:
        fh.write("done")

def extract_digits_from_component_version(component_str):
    version_re = re.compile(".*__(v.*)__.*")
    version_group = re.match(version_re, component_str).groups()[0]
    version_digits = int("".join([i for i in version_group if i.isdigit()]))
    return version_digits
datadump(
    snakemake.params.samplecomponent_ref_json,
)