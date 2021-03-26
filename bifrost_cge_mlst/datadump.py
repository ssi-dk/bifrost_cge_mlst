from bifrostlib import common
from bifrostlib.datahandling import Sample
from bifrostlib.datahandling import SampleComponentReference
from bifrostlib.datahandling import SampleComponent
from bifrostlib.datahandling import Component
from bifrostlib.datahandling import Category
from typing import Dict
import os


def extract_cge_mlst_report_and_details(sampleComponentObj):
    summary, results, file_path, key = sampleComponentObj.start_data_extraction("data.yaml")
    results[key] = datahandling.load_yaml(file_path)
    strains = []
    for mlst_db in results[key]:
        strain = results[key][mlst_db]["mlst"]["results"]["sequence_type"]
        strains.append(strain)
    results["strain"] = strains
    summary["strain"] = strains
    return (summary, results)


def generate_report(sampleComponentObj):
    summary, results, file_path, key = sampleComponentObj.start_data_extraction()
    key = sampleComponentObj.get_file_location_key("data.yaml")
    data = []
    for mlst_db in results[key]:
        strain = results[key][mlst_db]["mlst"]["results"]["sequence_type"]
        alleles = ", ".join([results[key][mlst_db]["mlst"]["results"]["allele_profile"][i]["allele_name"] for i in results[key][mlst_db]["mlst"]["results"]["allele_profile"]])
        data.append({
            "db": mlst_db,
            "strain": strain,
            "alleles": alleles
        })
    return data


# def datadump(sampleComponentObj, log):
#     sampleComponentObj.start_data_dump(log=log)
#     sampleComponentObj.run_data_dump_on_function(extract_cge_mlst_report_and_details, log=log)
#     sampleComponentObj.end_data_dump(generate_report_function=generate_report, log=log)

# datadump(
#     snakemake.params.sampleComponentObj,
#     snakemake.log)


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
        mlst['summary']['strain'].append(sequence_type) # maybe extend the string with subspec
        alleles = ", ".join(list(mlst_results['allele_profile'].keys()))
        mlst['report']['data'].append({
            "db":subspec,
            "strain":sequence_type,
            "alleles":alleles
        })
    results[file_key]['strain'] = mlst['summary']['strain']

def datadump(samplecomponent_ref_json: Dict):
    samplecomponent_ref = SampleComponentReference(value=samplecomponent_ref_json)
    samplecomponent = SampleComponent.load(samplecomponent_ref)
    sample = Sample.load(samplecomponent.sample)
    component = Component.load(samplecomponent.component)
    
    species_detection = sample.get_category("species_detection")
    species = species_detection["summary"].get("species", None)
    mlst_species = component["options"]["mlst_species_mapping"][species]

    mlst = samplecomponent.get_category("mlst")
    if mlst is None:
        mlst = Category(value={
                "name": "mlst",
                "component": {"id": samplecomponent["component"]["_id"], "name": samplecomponent["component"]["name"]},
                "summary": {"strain":[]},
                "report": {"data":[]}
            }
        )
    extract_mlst(mlst, samplecomponent["results"], samplecomponent["component"]["name"], mlst_species)
    samplecomponent.set_category(mlst)
    sample.set_category(mlst)
    common.set_status_and_save(sample, samplecomponent, "Success")
    
    with open(os.path.join(samplecomponent["component"]["name"], "datadump_complete"), "w+") as fh:
        fh.write("done")

datadump(
    snakemake.params.samplecomponent_ref_json,
)