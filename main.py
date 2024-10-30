import pdfplumber
# import re
import json

source_file = "data/The_Home_Depot_-_EDI_Specifications_and_Examples_-_Suppliers[1] (1).pdf" 
maintable_config = {
    'headers':["Pos", "Id", "Segment Name", "Req", "Max Use", "Repeat", "Notes", "Usage"]
}
maintable_data = {}
head_doors = {
    'ISA': 'Interchange Control Header',
    'GS': 'Functional Group Header',
    'GE': 'Functional Group Trailer',
    'IEA': 'Interchange Control Trailer'
}
big__titels = ["Heading", "Not Defined", 'Detail', 'tail']
loop__keys = ["LLOOOOPP", 'LOOP']
manu_page_number = 13

def int_checker(string_val):
    try:
        int(string_val)
        return True
    except ValueError:
        return False

def trim_string(string):
  return string.strip()

def clean_string_format(input_string):
    result, tt = [], []
    vv = input_string.split(" ")
    for r in vv:
        result = []
        for i, letter in enumerate(r):
            if i % 2 == 1:
                continue
            result.append(letter)
        tt.append(''.join(result))

    return ' '.join(tt)

def detail_process(data_list):
    """
        Process The details content for the Amnu table except
        except the envelope data. [ISA, GS, GE, IEA]
    """
    recovred_list = []
    inx = lambda v: next((i for i, e in enumerate(v) if len(e) == 1), -1)
    for i, seg in enumerate(data_list):
        first_elmnt = seg.split(" ")[0]
        if first_elmnt in loop__keys:
            recovred_list.append(clean_string_format(seg))
        elif int_checker(first_elmnt):
            recovred_list.append(seg)
        else:
            """
            This process is responsible for Converting thi two lines:
                '0100 LX Transaction Set Line M 1 N2/0100 Must use'
                'Number'
            to this on concatenated line:
                '0100 LX Transaction Set Line Number M 1 N2/0100 Must use'
            """
            previous_line = data_list[i-1].split(" ")
            previous_line.insert(inx(previous_line),  data_list[i])
            recovred_list.append(" ".join(previous_line))
            recovred_list.remove(data_list[i-1])
    
    return recovred_list

with pdfplumber.open(source_file) as pdf:

    # get the page for the manu content.
    first_page = pdf.pages[manu_page_number]
    table = first_page.extract_text().split("\n")
        
    try:
        idx = table.index("Not Defined:")
        table_content = table[idx:]  
        [print(x) for x in table_content]

    except ValueError:
        table_content = []  

    start_idx, end_idx = -1, -1
    processed = False
    
    # Data Separator - based on big__titels
    for i, e in enumerate(table_content):
        processed = False
        if start_idx == -1 and any(e.startswith(s) for s in big__titels):
            start_idx = i
            title =  table_content[i][:-1]
            processed = True 
        
        if not processed and any(e.startswith(x) for x in big__titels):
            end_idx = i
            maintable_config[title] = table_content[start_idx + 1: end_idx]
            start_idx = -1
        
        if e.startswith("IEA"):
            maintable_config["tail"] = table_content[end_idx + 1: i + 1]

    #Data Cleaning - when the maintable_config
    headers_ = " ".join(maintable_config["headers"])
    content = list(maintable_config.items())[1:]
    for key, value in list(maintable_config.items())[1:]:
        for e in value:
            if "".join(e) == headers_:
                value.remove(e)

    with open('bag_words.txt','r') as f:
        all_text = f.read().split("########")
        segment_name = all_text[0].split("\n")
        ids = all_text[1].split("\n")

    # Envelope data processing
    fixedTails = ["Must use", "Used"]
    maintable_config['table'] = []
    for k, v in content:
        if k in ["Not Defined", "tail"]:
            for x in v:
                c_val = x.split(" ")
                if not int_checker(head_doors[c_val[0]]):
                    leading = ['None', c_val[0],head_doors[c_val[0]]]
                    beg = c_val[0] + " " + head_doors[c_val[0]]
                    tail = x.split(beg)[1]
                    if "Must use" in tail:
                        tail = trim_string(tail.split("Must use")[0])
                        middle_values = tail.split(" ")
                        middle_values.append("Must use")
                    else:
                        tail = trim_string(tail.split("Must use")[0])
                        middle_values = tail.split(" ")
                        middle_values.append("Used")

                    leading.extend(middle_values)
                    maintable_config['table'].append(leading)
        else:
            d = detail_process(v)
            maintable_config['table'].append(d)

    with open("test.json", "w") as f:
        json.dump(maintable_config, f)

