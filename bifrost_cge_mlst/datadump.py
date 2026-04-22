from bifrostlib import common
from bifrostlib.datahandling import Sample
from bifrostlib.datahandling import SampleComponentReference
from bifrostlib.datahandling import SampleComponent
from bifrostlib.datahandling import Component
from bifrostlib.datahandling import Category
from typing import Dict
import os
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
        mlst['summary']['sequence_type'][subspec] = sequence_type
        loci = mlst_results['allele_profile'].keys()
        allele_dict = {locus: mlst_results['allele_profile'][locus]['allele'] for locus in loci}
        mlst['report']['data'].append({
            "db": subspec,
            "sequence_type": sequence_type,
            "alleles": allele_dict
        })
    results[file_key]['sequence_type'] = mlst['summary']['sequence_type']

def datadump(samplecomponent_id: str):
    #samplecomponent_ref = SampleComponentReference(value=samplecomponent_ref_json)
    samplecomponent_ref = SampleComponentReference(_id=samplecomponent_id)
    samplecomponent = SampleComponent.load(samplecomponent_ref)
    sample = Sample.load(samplecomponent.sample)
    component = Component.load(samplecomponent.component)

    database_path = (
        f"{os.environ['BIFROST_INSTALL_DIR']}/bifrost/components/"
        f"bifrost_{component['display_name']}/{component['resources']['database_path']}"
    )

    species_detection = sample.get_category("species_detection")
    species = species_detection["summary"].get("species", None)
    mlst_species = component["options"]["mlst_species_mapping"][species]

    try:
        db_repo = Repo(database_path)
        db_commit = str(db_repo.head.commit)
        print(f"db repo {db_repo}")
        print(f"db commit {db_commit}")
    except Exception:
        db_repo = "Error"
        db_commit = "Error"
        
    mlst = Category(value={
        "name": "mlst",
        "component": {
            "id": samplecomponent["component"]["_id"],
            "name": samplecomponent["component"]["name"]
        },
        "summary": {"sequence_type": {}},
        "report": {"data": []}
    })

    extract_mlst(mlst, samplecomponent["results"], samplecomponent["component"]["name"], mlst_species)

    mlst['database_versions'] = {
        'mlst_db': db_commit,
        'path': database_path
    }

    samplecomponent.set_category(mlst)

    # Always overwrite sample category without version comparison
    sample.set_category(mlst)

    common.set_status_and_save(sample, samplecomponent, "Success")

    with open(os.path.join(samplecomponent["component"]["name"], "datadump_complete"), "w+") as fh:
        fh.write("done")

datadump(
    snakemake.params.samplecomponent_id
)
