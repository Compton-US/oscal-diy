import os, json

from pathlib import Path
from oscalic import Helper

from faker import Faker
fake_it = Faker()

class Identifier:
    uuid = None
    name = None

class Relation:
    source = Identifier
    target = Identifier


########################################################################
#%% Export YAML file
def save_yaml(ssp, filepath_yaml):
    if os.path.exists(filepath_yaml):
        os.remove(filepath_yaml)
    Path(filepath_yaml).write_text(Helper.to_yaml(ssp))

    return True

#%% Export JSON file
def save_json(ssp, filepath_json):
    ssp_output = ssp.dict(by_alias=True,exclude_unset=True)

    if os.path.exists(filepath_json):
        os.remove(filepath_json)
    out_file = open(filepath_json, "w")
    json.dump(ssp_output, out_file, sort_keys=False)

    return True


########################################################################

# def get_ipsom_provided:
# source <- target
# provided <- inherited

# responsibility <- satisfied


# satisfied <- provided
# satisfied <- responsibility
# satisfied <- inherited

def get_related_uuids(target_name, source_name, source_uuid=None):
    rel = Relation
    rel.source.name = source_name
    rel.target.name = target_name

    rel.source.uuid = fake_it.uuid4()
    rel.target.uuid = fake_it.uuid4()

    if source_uuid:
        rel.source.uuid = source_uuid



    return rel
