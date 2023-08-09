#%%
import xml.etree.ElementTree as ET
filename='/home/users/v-surapoom/Workspaces/ile-de-france/scenarios/bau_capacity/v01network.xml'
# Load the XML file
tree = ET.parse(filename)
root = tree.getroot()

# Find and modify the desired <link> elements
for link_element in root.findall(".//link[@modes='car,car_passenger']"):
    capacity = float(link_element.get('capacity'))
    new_capacity = '{:.1f}'.format(capacity/2)
    link_element.set('capacity', new_capacity)

xml_file_path='/home/users/v-surapoom/Workspaces/ile-de-france/scenarios/bau_capacity/v01network_mutated.xml'

# Save the modified XML back to the file
tree.write(xml_file_path)
#%%
# Read the original XML content
with open(xml_file_path, 'r') as file:
    original_content = file.read()

# Create the XML declaration and DOCTYPE declarations
declaration = '<?xml version="1.0" encoding="UTF-8"?>'
doctype = '<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v2.dtd">'

# Set the declarations as the first two lines of the XML file
xml_content = f"{declaration}\n{doctype}\n{original_content}"

# Write the XML content to a file
with open(xml_file_path, 'w') as file:
    file.write(xml_content)
# %%
