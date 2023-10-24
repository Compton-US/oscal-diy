########################################################################
#%% Work with controls from: https://github.com/usnistgov/csv-synthetic-controls/

import pandas as pd
import datetime, json, yaml, os
import oscalic.schema as oscal
import tools as t

from pathlib import Path
from oscalic.system_security_plan import SystemSecurityPlan as SSP
from oscalic.control import ControlAssembly as Control, StatementAssembly as Statement, ByComponentAssembly as ByComponent
from oscalic import Template, Helper, Validation
from xsdata_pydantic.bindings import XmlParser, JsonParser

from pprint import pprint

error_condition = None
errors = list()

########################################################################



#%% Paths
dir_output = os.path.join(os.getcwd(), 'output')
dir_template = os.path.join(os.getcwd(), 'template')
dir_content = os.path.join(os.getcwd(), 'content')

filename_output = 'SSP.example'
filename_input = 'NIST_800-53_Rev5_Simulated.csv'

filepath_yaml = f"{dir_output}/{filename_output}.yaml"
filepath_json = f"{dir_output}/{filename_output}.json"
filepath_csv = f"{dir_content}/{filename_input}"

#%% Static Settings
ssp_system_name = 'Demonstration System with Synthetic Content'
ssp_reason = 'This SSP demonstrates exports using only the exports mechanism, and would require SSP model modifications.'

sep = '*'*100
lb = "\n\n"

########################################################################



#%% Setup
df = pd.read_csv(filepath_csv)
grouped_df = df.groupby('control_id')

this_system_component_uuid = str(Helper.get_uuid())
today = datetime.datetime.now()
today_format = '%Y-%m-%dT00:00:00.0000-04:00'
today = today.strftime(today_format)
control_list = list()

#%% Start SSP
ssp_template = 'template.ssp.yaml'
ssp_data = {
    'uuid:document':        str(Helper.get_uuid()),
    'uuid:statement':       str(Helper.get_uuid()),
    'uuid:component':       this_system_component_uuid, 
    'uuid:user':            str(Helper.get_uuid()),
    'uuid:party':           str(Helper.get_uuid()), 
    'uuid:by-component':    str(Helper.get_uuid()), 
    'uuid:information-type':str(Helper.get_uuid()), 
    'version':              '0.0.1',
    'modified_date':        f"{today}",
    'ssp_system_name':      ssp_system_name,
    'ssp_reason':           ssp_reason
}
ssp_content = Template.apply(ssp_template, ssp_data)
ssp = Helper.from_yaml(SSP, ssp_content)



########################################################################
#%% Build Content
for control_id, group in grouped_df:
    # if control_id == 'ac-2':
        print(control_id.upper())

        statements = list()
        for index, row in group.iterrows():
            components = list()
            
            # 'implementation-status': {
            #     'state': row['state'],
            #     'remarks': ''
            # }

            provided_uuid = str(Helper.get_uuid())
            provided_content = [{
                'uuid': provided_uuid,
                'description': row['export_provided'],

            }]

            responsibilities_content = [{
                'uuid': str(Helper.get_uuid()),
                'provided-uuid': provided_uuid,
                'description': row['export_responsibility']
            }]

            satisfied_content = [{
                'uuid': str(Helper.get_uuid()),
                'responsibility-uuid': str(Helper.get_uuid()),
                'description': row['export_responsibility']                 
            }]

            inherited_content = [{
                'uuid': str(Helper.get_uuid()),
                'provided-uuid': provided_uuid,
                # 'satisfied-uuid': satisfied_uuid,
                'description': row['export_responsibility']                 
            }]

            #############################################################
            # Deprecated
            # export_content = {
            #     'provided': provided_content,
            #     'responsibilities': responsibilities_content
            # } 

            #############################################################
            component_content = {
                'component_uuid': this_system_component_uuid,
                'uuid': str(Helper.get_uuid()),
                'description': row['description'],
                'provided': provided_content,
                'responsibilities': responsibilities_content,
                'satisfied': satisfied_content,
                'inherited':inherited_content
                # 'export': export_content
            }
            component = ByComponent.construct(**component_content)
            components.append(component)

            #############################################################
            statement_content = {
                'statement_id': row['statement_id'],
                'uuid': str(Helper.get_uuid()),
                'by_components': components
            }
            statement = Statement.construct(**statement_content)
            statements.append(statement)

        control_content = {
            'uuid': str(Helper.get_uuid()),
            'control_id': row['control_id'],
            'statements': statements
        }

        try:
            control = Control.construct(**control_content)
            output = Helper.to_yaml(control)
            ssp.system_security_plan.control_implementation.implemented_requirements.append(control)
        except Validation.OSCALValidationError as e:
            errors.append(e.json())
            error_condition = 1




########################################################################
#%% Export YAML file
t.save_yaml(ssp,filepath_yaml)

#%% Export JSON file
t.save_json(ssp,filepath_json)



# %% Validation
# Validate/oscal-cli-1.0.2 ssp validate output/SSP.exports.example.a.json >ssp.txt 2>&1

## python ssp.py
## Validate/oscal-cli-1.0.2 ssp validate output/SSP.exports.example.a.json
## Validate/oscal-cli-1.0.2 ssp validate output/SSP.exports.example.a.yaml