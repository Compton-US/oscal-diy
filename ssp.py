########################################################################
#%% Work with controls from: https://github.com/usnistgov/csv-synthetic-controls/

import os
import pandas as pd
import tools as t

########################################################################

error_condition             = None
errors                      = list()

#%% Paths os.getcwd()
dir_output                  = os.path.join(os.getcwd(),'output')
dir_template                = os.path.join(os.getcwd(),'templates')
dir_content                 = os.path.join(os.getcwd(),'content')

filename_output             = 'example'
filename_input              = 'NIST_800-53_Rev5_Simulated.csv'

filepath_csv                = os.path.join(dir_content, filename_input)

#%% Static Settings
sep                         = '*'*100
lb                          = "\n\n"

#%% Setup
df_content                  = pd.read_csv(filepath_csv)
grouped_df                  = df_content.groupby('control_id')

#%% Load all templates
templates = []
for root, dirs, files in os.walk(dir_template):
    for file in files:
        if file.endswith(".yaml"):
             templates.append(file)

########################################################################

org_metadata = {}


org_metadata['csp'] = {
    'version':              '0.0.1',
    'ssp_system_name':      'Demonstration System representing a Cloud Service Provider',
    'ssp_reason':           'This SSP demonstrates prototype modeling for sharing of responsibility.'   
}

org_metadata['msp'] = {
    'version':              '0.0.1',
    'ssp_system_name':      'Demonstration System representing a Managed Service Provider',
    'ssp_reason':           'This SSP demonstrates prototype modeling for sharing of responsibility.'   
}

org_metadata['app'] = {
    'version':              '0.0.1',
    'ssp_system_name':      'Demonstration System representing an Application Owner',
    'ssp_reason':           'This SSP demonstrates prototype modeling for sharing of responsibility.'       
}

   

#%% Build SSPs
for ssp_template in templates:
    current_org                 = ssp_template.split('.')[2:-1][0]
    filepath_template           = os.path.join(dir_template,ssp_template)
    filepath_yaml               = os.path.join(dir_output, f"{filename_output}.{'.'.join(ssp_template.split('.')[1:-1])}.yaml")
    filepath_json               = os.path.join(dir_output, f"{filename_output}.{'.'.join(ssp_template.split('.')[1:-1])}.json")

    print(f"Generating [{current_org}]: {filepath_template}")
    print(f"YAML: {filepath_yaml}")
    print(f"JSON: {filepath_json}\n\n")

    metadata = org_metadata[current_org]

    # Build Content
    print("Building SSP")
    ssp = t.build_ssp(filepath_template, metadata, grouped_df)

    # Export YAML file
    print(f"YAML: {filepath_yaml}")
    t.save_yaml(ssp, filepath_yaml)

    # Export JSON file
    print(f"JSON: {filepath_json}")
    t.save_json(ssp, filepath_json)

    print(f"Validate/oscal-cli-1.0.2 ssp validate {filepath_yaml}")
    print(f"Validate/oscal-cli-1.0.2 ssp validate {filepath_json}")

    print("\n\n")



########################################################################
# %% Validation
# Validate/oscal-cli-1.0.2 ssp validate output/SSP.exports.example.a.json >ssp.txt 2>&1

## python ssp.py
## Validate/oscal-cli-1.0.2 ssp validate output/SSP.exports.example.a.json
## Validate/oscal-cli-1.0.2 ssp validate output/SSP.exports.example.a.yaml