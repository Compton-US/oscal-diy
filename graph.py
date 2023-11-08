#%% Load Libraries
from tools import Action
from pathlib import Path

import yaml
import re, os
import pandas as pd

act = Action()

# Create Graph
colors = {
    'default':          '#cc0000',

    # Identifiers
    'uuid':             '#a6e6fc',
    'ref-uuid':         '#c3fca6',

    # Responses
    'provided':         '#a6e6fc',
    'inherited':        '#62d8ff',
    'responsibilities': '#c0a6fc',
    'satisfied':        '#6296ff',

    # Document
    'model':            '#f89f9b',
    'control':          '#FFC355',
    'statement':        '#FBE29d',

    'line':             '#002481',
    'line_alt':         '#cccccc'
}

show_document_level     = True
show_control_level      = True
show_statement_level    = True
show_edges              = True
link_documents          = False
plot_associations       = False

show_documents          = ['ssp'] #,'crm']
show_responses          = ['provided', 'inherited', 'responsibilities', 'satisfied']

#%% Generate
output = []
diagram = {"nodes": [],"edges": []}
files = ['test.csv']

df_rels = pd.read_csv(files[0])

#%%
df_rels.head(10)

if show_document_level:
    diagram['nodes'].append({
        "id": "root_ssp_csp", 
        "label": 'SSP: CSP', 
        "type":"model", 
        "file_type":"OSCAL"
    })

    diagram['nodes'].append({
        "id": "root_ssp_msp", 
        "label": 'SSP: MSP', 
        "type":"model", 
        "file_type":"OSCAL"
    })

    diagram['nodes'].append({
        "id": "root_ssp_app", 
        "label": 'SSP: APP', 
        "type":"model", 
        "file_type":"OSCAL"
    })

    diagram['nodes'].append({
        "id": "root_crm_csp", 
        "label": 'CRM: CSP', 
        "type":"model", 
        "file_type":"OSCAL"
    })

    diagram['nodes'].append({
        "id": "root_crm_msp", 
        "label": 'CRM: MSP', 
        "type":"model", 
        "file_type":"OSCAL"
    })

    diagram['nodes'].append({
        "id": "root_crm_app", 
        "label": 'CRM: APP', 
        "type":"model", 
        "file_type":"OSCAL"
    })

# Controls
for index, row in df_rels.iterrows():
    if row['uuid'] not in diagram['nodes']:
        label = row['control'].upper()

        control_rel = act.b64(f"{row['source']}{row['document']}{row['control']}")

        if show_control_level:
            diagram['nodes'].append({
                "id": control_rel, 
                "label": label, 
                "type":"control", 
                "file_type":"ctl"
            })

        if show_edges:
            diagram['edges'].append({
                "source": f"root_{row['document']}_{row['source']}",
                "target": control_rel,
                "used_by": row['source'],
                "rel": row['document']
                })
        
# Statements
for index, row in df_rels.iterrows():
    if row['uuid'] not in diagram['nodes']:
        label = row['statement'].upper()

        control_rel = act.b64(f"{row['source']}{row['document']}{row['control']}")
        statement_rel = act.b64(f"{row['source']}{row['document']}{row['statement']}")

        if show_statement_level:
            diagram['nodes'].append({
                "id": statement_rel, 
                "label": label, 
                "type":"statement", 
                "file_type":"stmt"
            })

        if show_edges:
            diagram['edges'].append({
                "source": control_rel,
                "target": statement_rel,
                "used_by": row['source'],
                "rel": row['document']
                }) 

#%% Add statement response nodes
for index, row in df_rels.iterrows():
    if row['document'] in show_documents:
        if row['uuid'] not in diagram['nodes']:
            if row['relation'].lower() in show_responses:
                label = f"{row['statement']}:{row['relation']}:{row['source']}".upper()
                diagram['nodes'].append({
                    "id": row['uuid'], 
                    "label": label, 
                    "type":row['relation'].lower(), 
                    "file_type":row['document']
                })

if plot_associations:
    for index, row in df_rels.iterrows():
        if row['document'] in show_documents:
            if row['a_uuid'] not in diagram['nodes'] and isinstance(row['a_uuid'], str):
                if row['relation'].lower() in show_responses:
                    label = f"{row['statement']}:{row['relation']}:{row['source']}".upper()
                    diagram['nodes'].append({
                        "id": row['a_uuid'], 
                        "label": label, 
                        "type":row['relation'].lower(), 
                        "file_type":row['document']
                    })


#%%
for index, row in df_rels.iterrows():
    if show_edges:
        if row['document'] in show_documents:
            statement_rel = act.b64(f"{row['source']}{row['document']}{row['statement']}")
            diagram['edges'].append({
                "source": statement_rel,
                "target": row['uuid'],
                "used_by": row['source'],
                "rel": row['document']
                }) 

            if isinstance(row['a_uuid'], str):
                diagram['edges'].append({
                    "source": row['a_uuid'],
                    "target": row['uuid'],
                    "used_by": row['source'],
                    "rel": row['document'],
                    "style": 'line_alt'
                    }) 


# for index, row in df_rels.iterrows():
# # Link Documents
if link_documents:
    if row['document'] in show_documents:
        for index, row in df_rels.iterrows():
            if isinstance(row['a_uuid'], str):
                diagram['edges'].append({
                    "source": row['uuid'],
                    "target": row['a_uuid'],
                    "used_by": row['source'],
                    "rel": row['document']
                    }) 

#%%
output.append(act.diagram_markdown("Workflow", f"UUID_Relationships.graph"))

#%%
mkdn = 'output/Project.workflows.md'
if os.path.isfile(mkdn):
    os.unlink(mkdn)

#%%
act.make_diagram(diagram, colors=colors, filename=f"UUID_Relationships.graph")
act.save_markdown(output)
