from bifrostlib import common
yaml_obj = common.get_yaml('/bifrost/components/bifrost_cge_mlst/cge_mlst__v2_2_2/data.yaml')
print(yaml_obj['saureus']['mlst']['results'].keys())