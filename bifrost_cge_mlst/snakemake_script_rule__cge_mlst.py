# script for use with snakemake
import subprocess
import traceback
from bifrostlib import common
from bifrostlib.datahandling import Component, Sample
from bifrostlib.datahandling import SampleComponentReference
from bifrostlib.datahandling import SampleComponent
from typing import Dict
import os
from pathlib import Path

def run_cmd(command, log):
    with open(log.out_file, "a+") as out, open(log.err_file, "a+") as err:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        command_log_out, command_log_err = process.communicate()
        out.write((command_log_out or b"").decode())
        err.write((command_log_err or b"").decode())
        
def check_db(db_path, mlst_entry, log):
    checkpath = Path(db_path, mlst_entry)
    if not checkpath.exists():
        with open(log.err_file, "a+") as err:
            err.write(f"MLST db path {checkpath} does not exist")
        return False
    return True

def rule__run_cge_mlst(input, output, samplecomponent_ref_json, log):
    try:
        samplecomponent_ref = SampleComponentReference(value=samplecomponent_ref_json)
        samplecomponent = SampleComponent.load(samplecomponent_ref)
        sample = Sample.load(samplecomponent.sample)
        component = Component.load(samplecomponent.component)

        bifrost_install_dir = os.environ['BIFROST_INSTALL_DIR']
        database_path = f"{bifrost_install_dir}/bifrost/components/bifrost_{component['display_name']}/{component['resources']['database_path']}"

        contigs = input.contigs
        output_file = output.complete

        species_detection = sample.get_category("species_detection")
        species = species_detection["summary"].get("species", None)

        if species not in component["options"]["mlst_species_mapping"]:
            run_cmd(f"touch {component['name']}/no_mlst_species_DB", log)
        else:
            mlst_species = component["options"]["mlst_species_mapping"][species]
            data_dict = {}
            for mlst_entry in mlst_species:
                if not check_db(database_path, mlst_entry, log):
                    continue
                mlst_entry_path = f"{component['name']}/{mlst_entry}"
                run_cmd(f"rm -rf {mlst_entry_path}; mkdir {mlst_entry_path}", log)
                run_cmd(
                    f"mlst.py -x -matrix -s {mlst_entry} -p {database_path} "
                    f"-mp blastn -i {contigs} -o {mlst_entry_path}",
                    log
                )
                data_dict[mlst_entry] = common.get_yaml(f"{mlst_entry_path}/data.json")

            common.save_yaml(data_dict, output_file)

    except Exception:
        with open(log.err_file, "a+") as fh:
            fh.write(traceback.format_exc())

rule__run_cge_mlst(
    snakemake.input,
    snakemake.output,
    snakemake.params.samplecomponent_ref_json,
    snakemake.log)
