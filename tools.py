import datetime, os, json

from pathlib import Path
from oscalic import Helper

from faker import Faker
fake_it = Faker()


from oscalic.system_security_plan       import SystemSecurityPlan as SSP
from oscalic.control                    import ControlAssembly as Control
from oscalic.control                    import StatementAssembly as Statement
from oscalic.control                    import ByComponentAssembly as ByComponent
from oscalic                            import Template, Helper, Validation

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


def build_ssp(filepath_template, metadata, controls):

    this_system_component_uuid  = str(Helper.get_uuid())
    today                       = datetime.datetime.now()
    today_format                = '%Y-%m-%dT00:00:00.0000-04:00'
    today                       = today.strftime(today_format)

    ssp_data = {
        'uuid:component':       this_system_component_uuid,
        'uuid:document':        str(Helper.get_uuid()),
        'uuid:statement':       str(Helper.get_uuid()),
        'uuid:user':            str(Helper.get_uuid()),
        'uuid:party':           str(Helper.get_uuid()), 
        'uuid:by-component':    str(Helper.get_uuid()), 
        'uuid:information-type':str(Helper.get_uuid()), 
        'modified_date':        f"{today}",
    }
    ssp_data.update(metadata)

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


        control = Control.construct(**control_content)
        ssp.system_security_plan.control_implementation.implemented_requirements.append(control)


    return ssp
