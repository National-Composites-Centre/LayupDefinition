#write materials into new JSON format
from jsonic import serialize, deserialize
from utilities import sharpness , clean_json 

import CompositeStandard as cs

D = cs.CompositeDB()
D.allMaterials = []

with open("D:\CAD_library_sampling\TestCad_SmartDFM\X\LD_layup_database.txt","r") as fl:
    o= fl.read()

    for line in o.split("\n")[:]:
        m = cs.Material()
        m.materialName = line.split(",")[1]
        m.E1 = line.split(",")[2]
        m.E2 = line.split(",")[3]
        m.G12 = line.split(",")[4]
        m.G23 = line.split(",")[5]
        m.v12 = line.split(",")[6]
        m.infoSource = line.split(",")[7]
        m.thickness = line.split(",")[8]
        m.density = line.split(",")[9]
        m.permeability_1 = line.split(",")[10]
        m.type = line.split(",")[11]
        D.allMaterials.append(m)

json_str = serialize(D, string_output = True)

json_str = clean_json(json_str)
# Print the JSON string
print(json_str)

#json_str = cleandict(json_str)

#save as file
with open("D:\CAD_library_sampling\TestCad_SmartDFM\X\LD_layup_database.json", 'w') as out_file:
    out_file.write(json_str)

        
