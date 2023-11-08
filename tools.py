import datetime, os, json, subprocess

from pathlib import Path
from oscalic import Helper

from faker import Faker
fake_it = Faker()


from oscalic.system_security_plan       import SystemSecurityPlan as SSP
from oscalic.component_definition       import ComponentDefinition as CDef
from oscalic.control                    import StatementAssembly as Statement
from oscalic.control                    import ByComponentAssembly as ByComponent
from oscalic.control                    import ControlAssembly as Control
from oscalic                            import Template, Helper, Validation
from oscalic.common                     import SatisfiedAssembly, ResponsibilitiesAssembly, InheritedAssembly, ProvidedAssembly
class Identifier:
    uuid = None
    name = None

class Relation:
    source = Identifier
    target = Identifier




########################################################################

from pydantic import BaseModel, Field
from typing import List

class IdRecord(BaseModel):
    source: str = Field(default=None)
    document: str = Field(default=None)
    control: str = Field(default=None)
    statement: str = Field(default=None)
    relation: str = Field(default=None)
    uuid_name: str = Field(default=None)
    uuid: str = Field(default=None)
    a_uuid_name: str = Field(default=None)
    a_uuid: str = Field(default=None)

class IdCollection(BaseModel):
    records: List[IdRecord] = Field(default=[])
    
record_list = []
record_collection = IdCollection()

########################################################################

all_model_metadata = {
    'oscal_version': '1.1.1'
}

filler_word_list=['sample', 'security', 'content', 'response', 'explanation', 'identifying']

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
    json.dump(ssp_output, out_file, sort_keys=False, indent=2)

    return True

def clean_output(dir):
    for filename in os.listdir(dir):
        ext = filename.split('.')[-1]
        if ext in ['json','xml','yaml','log']:
            os.remove(os.path.join(dir,filename))

def random_prose(input, length=10):
    words = input.split()
    result = fake_it.sentence(nb_words=length, ext_word_list=words)

    return result

def get_marker_uuid(marker):
    id = str(Helper.get_uuid())
    start = len(marker) - 1
    return marker.upper() + id[start:len(id)]

########################################################################
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


def get_components(document, statement_id=None):
    components = []
    # print(document)
    for requirement in document.implemented_requirements:
        for statement in requirement.statements:
            if statement_id:
                if statement.statement_id == statement_id:
                    for component in statement.by_components:
                        components.append(component)
            else:
                for component in statement.by_components:
                    components.append(component)
    return components


def get_inherited_responses(crm, statement_id=None, marker=''):
    crm_inherited_content = []
    crm_satisfied_content = []
    
    crm_components = get_components(crm.responsibility_sharing.capabilities[0]['control_implementation'], statement_id)

    for component in crm_components:
        if 'provided' in dir(component):
            crm_inherited_content.append({
                'uuid': get_marker_uuid(marker),
                'provided-uuid': component.provided[0]['uuid'],
                # 'satisfied-uuid': satisfied_uuid,
                'description': ''
                    + component.provided[0]['description']            
            })

        if 'responsibilities' in dir(component):
            crm_satisfied_content.append({
                'uuid': get_marker_uuid(marker),
                'responsibility-uuid': component.responsibilities[0]['uuid'],
                'description': ''
                    + component.responsibilities[0]['description'] 
                    + ' (Random SATISFIED Content Follows) ' 
                    + random_prose(component.responsibilities[0]['description'])     
            })

    return (crm_inherited_content,crm_satisfied_content)

def build_ssp(filepath_template, metadata, controls=None, crm=None):
    current_org_type            = filepath_template.split('.')[2:-1][0]
    this_system_component_uuid  = get_marker_uuid(current_org_type)
    today                       = datetime.datetime.now()
    today_format                = '%Y-%m-%dT00:00:00.0000-04:00'
    today                       = today.strftime(today_format)

    ssp_data = {
        'uuid:component':       this_system_component_uuid,
        'uuid:document':        get_marker_uuid(current_org_type),
        'uuid:statement':       get_marker_uuid(current_org_type),
        'uuid:user':            get_marker_uuid(current_org_type),
        'uuid:party':           get_marker_uuid(current_org_type), 
        'uuid:by-component':    get_marker_uuid(current_org_type), 
        'uuid:information-type':get_marker_uuid(current_org_type), 
        'modified_date':        f"{today}"
    }
    ssp_data.update(metadata)
    ssp_data.update(all_model_metadata)

    ssp_content = Template.apply(filepath_template, ssp_data)
    ssp         = Helper.from_yaml(SSP, ssp_content)





    for control_id, group in controls:
        # if control_id == 'ac-2':
            # print(control_id.upper())

        statements = list()
        for index, row in group.iterrows():
            components = list()
            
            # 'implementation-status': {
            #     'state': row['state'],
            #     'remarks': ''
            # }

            ##### PROVIDED ##############################################
            provided_uuid = get_marker_uuid(current_org_type)
            provided_content = [{
                'uuid': provided_uuid,
                'description': row['export_provided'] 
                                    + ' (Random Content Follows) ' 
                                    + random_prose(row['export_provided']),
                'exportable': True
            }]

            # Track Connections
            record = {
                'source': current_org_type,
                'document': 'ssp',
                'control': control_id,
                'statement': row['statement_id'],
                'relation': 'provided',
                'uuid_name': 'provided-uuid',
                'uuid': provided_uuid,
                'a_uuid_name': '',
                'a_uuid': ''
            }
            record_list.append(IdRecord(**record))
            # End Track Connections

            ##### RESPONSIBILITIES ##############################################
            responsibilities_uuid = get_marker_uuid(current_org_type)
            responsibilities_content = [{
                'uuid': responsibilities_uuid,
                'provided-uuid': provided_uuid,
                'description': row['export_responsibility'],
                'exportable': True
            }]
            
            # Track Connections
            record = {
                'source': current_org_type,
                'document': 'ssp',
                'control': control_id,
                'statement': row['statement_id'],
                'relation': 'responsibilities',
                'uuid_name': 'responsibilities-uuid',
                'uuid': responsibilities_uuid,
                'a_uuid_name': 'provided_uuid',
                'a_uuid': provided_uuid
            }
            record_list.append(IdRecord(**record))
            # End Track Connections

            ##### SATISFIED ##############################################
            satisfied_uuid = get_marker_uuid(current_org_type)
            satisfied_content = [{
                'uuid': satisfied_uuid,
                'responsibility-uuid': responsibilities_uuid,
                'description': row['export_responsibility'] 
                                    + ' (Random Content Follows) ' 
                                    + random_prose(row['export_provided'])     
            }]

            # Track Connections
            record = {
                'source': current_org_type,
                'document': 'ssp',
                'control': control_id,
                'statement': row['statement_id'],
                'relation': 'satisfied',
                'uuid_name': 'satisfied-uuid',
                'uuid': satisfied_uuid,
                'a_uuid_name': 'responsibilities_uuid',
                'a_uuid': responsibilities_uuid
            }
            record_list.append(IdRecord(**record))
            # End Track Connections


            crm_inherited_content = []
            crm_satisfied_content = []
            if crm:
                #print(f"Get inherited for {row['statement_id']}")
                (crm_inherited_content, crm_satisfied_content) = get_inherited_responses(crm, row['statement_id'], current_org_type)

            
            if len(crm_satisfied_content) > 0:
                satisfied_content.extend(crm_satisfied_content)


            ##### INHERITED ##############################################
            inherited_content = None
            if '.csp.' not in filepath_template:
                inherited_uuid = get_marker_uuid(current_org_type)
                inherited_content = [{
                    'uuid': inherited_uuid,
                    'provided-uuid': provided_uuid,
                    # 'satisfied-uuid': satisfied_uuid,
                    'description': row['export_responsibility']                 
                }]
                
                if len(crm_inherited_content) > 0:
                    inherited_content.extend(crm_inherited_content)


                #print(IdCollection, dir(IdCollection))

                # Track Connections
                record = {
                    'source': current_org_type,
                    'document': 'ssp',
                    'control': control_id,
                    'statement': row['statement_id'],
                    'relation': 'inherited',
                    'uuid_name': 'inherited-uuid',
                    'uuid': inherited_uuid,
                    'a_uuid_name': 'provided-uuid',
                    'a_uuid': provided_uuid
                }
                record_list.append(IdRecord(**record))
                # End Track Connections
                

            #############################################################
            # Deprecated
            # export_content = {
            #     'provided': provided_content,
            #     'responsibilities': responsibilities_content
            # } 

            #############################################################
            component_content = {
                'component_uuid': this_system_component_uuid,
                'uuid': get_marker_uuid(current_org_type),
                'description': "DO NOT SHARE - " + row['description'],
                'provided': provided_content,
                'responsibilities': responsibilities_content,
                'satisfied': satisfied_content
                # 'export': export_content
            }

            if inherited_content:
                component_content['inherited'] = inherited_content

            component = ByComponent.construct(**component_content)
            components.append(component)

            #############################################################
            statement_content = {
                'statement_id': row['statement_id'],
                'uuid': get_marker_uuid(current_org_type),
                'by_components': components
            }
            statement = Statement.construct(**statement_content)
            statements.append(statement)

        control_content = {
            'uuid': get_marker_uuid(current_org_type),
            'control_id': row['control_id'],
            'statements': statements
        }


        control = Control.construct(**control_content)
        ssp.system_security_plan.control_implementation.implemented_requirements.append(control)

    return ssp




def build_crm(filepath_template, ssp):
    current_org_type= filepath_template.split('.')[2:-1][0]
    today           = datetime.datetime.now()
    today_format    = '%Y-%m-%dT00:00:00.0000-04:00'
    today           = today.strftime(today_format)

    crm_data = {
        'crm_title':        "Customer Responsibility Matrix",
        'uuid:document':    get_marker_uuid(current_org_type),
        'uuid:component':   get_marker_uuid(current_org_type), 
        'modified_date':    f"{today}",
    }
    crm_data.update(all_model_metadata)
    crm_data.update(ssp.system_security_plan.metadata.dict())
    crm_data.update(ssp.system_security_plan.metadata.dict())

    crm_content     = Template.apply(filepath_template, crm_data)
    crm = Helper.from_yaml(CDef, crm_content)

    # Loop through each requirement in the ssps and export the exportable.
    # for requirement in ssp.system_security_plan.control_implementation.implemented_requirements:
    #     for statements in requirement.statements:
    
    for component in get_components(ssp.system_security_plan.control_implementation):
        if 'provided' in dir(component):
            if not ('exportable' in component.provided[0] and \
            component.provided[0]['exportable'] == True):
                del component.provided

        if 'responsibilities' in dir(component):
            if not ('exportable' in component.responsibilities[0] and \
            component.responsibilities[0]['exportable'] == True):
                del component.responsibilities

        if 'satisfied' in dir(component):
            if not ('exportable' in component.satisfied[0] and \
            component.satisfied[0]['exportable'] == True):
                del component.satisfied

        if 'inherited' in dir(component) and component.inherited != None:
            if not ('exportable' in component.inherited[0] and \
            component.inherited[0]['exportable'] == True):
                del component.inherited

    crm.responsibility_sharing.capabilities=[{
        'uuid': get_marker_uuid(current_org_type),
        'name': 'Statement of Shared Responsibility',
        'description': 'This is a demonstration CRM.',
        'control_implementation': ssp.system_security_plan.control_implementation
    }]

    return crm
