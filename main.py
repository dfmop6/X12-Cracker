import pdfplumber


source_file = "data/The_Home_Depot_-_EDI_Specifications_and_Examples_-_Suppliers[1] (1).pdf" 

maintable_config = {
    'headers':["Pos", "Id", "Segment Name", "Req", "Max Use", "Repeat", "Notes", "Usage"]
}
big__titels = ["Heading", "Not Defined", 'Detail', 'tail']

with pdfplumber.open(source_file) as pdf:
    # for page in pdf.pages[13]:        
    #     print(page.extract_text()) 

    first_page = pdf.pages[13]
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
    
    for key, value in list(maintable_config.items())[1:]:
        for e in value:
            if "".join(e) == headers_:
                value.remove(e)

    print(maintable_config)