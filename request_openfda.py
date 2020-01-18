import requests
from string import Template
import urllib.request as urllib2
import os
import requests
from urllib.parse import urlparse
#import urllib.request.urlretrieve
import urllib.request
import pprint as pp

def download_url(url):
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: %s Bytes: %s" % (file_name, file_size))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print(status)

    f.close()

    
def download_data_files(years=None):
    """
    years (list): if presents, it's a list of years to download
       [should be from 2004 to 2019]
    """
    if years is None:
        years = []
    url = "https://api.fda.gov/download.json"
    data = requests.get(url).json()
    print("Categories of data: ", data["results"].keys())
    print("Subgroups in 'drug' category: ", data["results"]["drug"].keys())
    #pp.pprint(data["results"]["drug"]["event"])
    data_root = "./data"
    for x in data["results"]["drug"]["event"]["partitions"]:
        path = os.path.join(data_root, x["display_name"])
        skip_download = True
        for yr in years:
            if isinstance(yr, int):
                yr = str(yr)
            if yr in x["display_name"]:
                # download this file
                # print("download ", x["display_name"])
                skip_download = False
                break
 
        if skip_download and len(years) > 0:
            continue
        if not os.path.exists(path):
            os.makedirs(path)
        url = x["file"]
        url_path = urlparse(url)
        file_name = os.path.join(path, os.path.basename(url_path.path))
        size_mb = x["size_mb"]
        try:
            if os.path.getsize(file_name) > 0:
                # Non empty file exists
                # statinfo = os.stat(file_name)
                statinfo = os.stat(file_name)
                if round(statinfo.st_size / (1024*1024), 2) != size_mb:
                    print("Downloading ", x)
                    urllib.request.urlretrieve(url, file_name)
                else:
                    print("Completed ", file_name)
            else:
                # Empty file exists
                print("Downloading ", x)
                urllib.request.urlretrieve(url, file_name)
        except OSError as e:
            print("Downloading ", x)
            urllib.request.urlretrieve(url, file_name)
        # print(file)
        # print(path)
        print("Completed ", x)

    
def get_searchable_fields(searchable_fields, field_dict, prefix="", print_level=None):
    """
    convert yaml fields into searchable fields, i.e. a.b.c
    """
    def iter_get_field(searchable_fields, field_dict, prefix, level):
        # print(json.dumps(attr_list, indent=1))
        func = iter_get_field
        for key, val in field_dict["properties"].items():
            if print_level is not None and level == print_level:
                print(prefix, ": ", key)
            field = key
            old_prefix = prefix
            if "properties" not in val:
                old_prefix_1 = prefix
                if "type" in val and val["type"] == "array":
                    prefix = prefix + "." + field
                    # get_searchable_fields(searchable_fields, val["items"], prefix)
                    # print(prefix, val["items"]["properties"].keys())
                    if "properties" in val["items"]:
                        for element, value in val["items"]["properties"].items():
                            if "type" in value and value["type"] == "object":
                                old_prefix_2 = prefix
                                prefix += "." + element
                                # print(prefix)
                                # pp.pprint(value)
                                func(searchable_fields, value, prefix, level+1)
                                prefix = old_prefix_2
                            else:
                                searchable_fields.append(prefix+"."+element)
                    else:
                        searchable_fields.append(prefix)
                else:
                    if len(prefix) > 0:
                        searchable_fields.append(prefix+"."+field)
                    else:
                        searchable_fields.append(field)
                prefix = old_prefix_1
                #print(field)
            else:
                old_prefix_1 = prefix
                if len(prefix) > 0:
                    prefix += "." + field
                else:
                    prefix = field
                func(searchable_fields, val, prefix, level+1)
                prefix = old_prefix_1
            prefix = old_prefix
    level = 1
    iter_get_field(searchable_fields, field_dict, prefix, level)
    return


def map_index_to_value(attr_list, searchable_fields, index):
    """ get the exact value for certain field that use index
    Args:
        searchable_field (str): in the form of a.b.c
        attr_list (list): the list of all attributes
        index (int): 

    Return:    
        if not mapping is found: return the unfound key as value
    """
    fields = searchable_fields.split('.')
    x = attr_list
    for val in fields:
        if "type" in x and x["type"] == "array":
            x = x["items"]["properties"][val]
        else:
            x = x["properties"][val]
    x = x["possible_values"]
    if x["type"] == "one_of":
        zfill = len(next(iter(x["value"])))
        try:
            result = (x["value"][str(index).zfill(zfill)])
        except KeyError:
            result = str(index).zfill(zfill)
    return result


def query_count_drug_indication(count_field="patient.drug.drugindication.exact",
                                exact=False,
                                receivedate="20040101+TO+20160601", 
                                extra_terms=None):
    fields = {}
    API_KEY = open("openfda_key.txt").read().rstrip()
    fields["API_KEY"]=API_KEY

    DATE_FROM=""
    DATE_TO=""

    # Date-time range
    #SEARCH_TERMS="receivedate:[20040101+TO+20160601]"
    SEARCH_TERMS="receivedate:[{range}]".format(range=receivedate)
    #SEARCH_TERMS="patient.drug.drugindication"
    if extra_terms is not None and len(extra_terms) > 0:
        fields["SEARCH_TERMS"]=SEARCH_TERMS+"+AND+"+extra_terms
    else:
        fields["SEARCH_TERMS"]=SEARCH_TERMS

    SORT_FIELD=""
    # SORT_FIELD="fieldname:desc"
    # SORT_FIELD="fieldname:asc"
    fields["SORT_FIELD"]=SORT_FIELD

    # Fix count_field
    if count_field == "primarysource":
        count_field = "primarysourcecountry"
    COUNT_FIELD=""
    #COUNT_FIELD="receivedate"
    COUNT_FIELD=count_field
    if exact and not COUNT_FIELD.endswith(".exact"):
        COUNT_FIELD += ".exact"
    fields["COUNT_FIELD"] = COUNT_FIELD
  
    SKIP_NUM_REC=""
    fields["SKIP_NUM_REC"]=SKIP_NUM_REC

    LIMIT_REC=""
    fields["LIMIT_REC"]=LIMIT_REC

    template = Template('https://api.fda.gov/drug/event.json?api_key=$API_KEY&search=$SEARCH_TERMS&sort=$SORT_FIELD&limit=$LIMIT_REC&skip=$SKIP_NUM_REC&count=$COUNT_FIELD')
    #template = Template('https://api.fda.gov/drug/event.json?api_key=$API_KEY&limit=1')

    URL = template.substitute(**fields)
    print(URL)

    data = requests.get(URL).json()
    return data


def query_drug_events(receivedate="20040101+TO+20160601", country="UK", 
                      limit=99, skip=0, find_all=False):
    """
    query records within a date range
      coming from a given country or all countries
    
    paging is supported to request exceeding the limit set by FDA which is 99 records
    
    """
    fields = {}
    API_KEY = open("openfda_key.txt").read().rstrip()
    fields["API_KEY"]=API_KEY

    DATE_FROM=""
    DATE_TO=""

    SEARCH_TERMS = {}
    # Date-time range
    #SEARCH_TERMS="receivedate:[20040101+TO+20160601]"
    if len(receivedate) > 0:
        SEARCH_TERMS["receivedate"]="receivedate:[{range}]".format(range=receivedate)
    if len(country) > 0:
        SEARCH_TERMS["occurcountry"]="occurcountry:{CODE}".format(CODE=country)
  
    #SEARCH_TERMS="patient.drug.drugindication"
    fields["SEARCH_TERMS"] = ""
    for key, val in SEARCH_TERMS.items():
        fields["SEARCH_TERMS"] += val + "+AND+"
    if len(SEARCH_TERMS) > 0:
        fields["SEARCH_TERMS"] = fields["SEARCH_TERMS"][:-5]

    SORT_FIELD=""
    # SORT_FIELD="fieldname:desc"
    # SORT_FIELD="fieldname:asc"
    fields["SORT_FIELD"]=SORT_FIELD

    COUNT_FIELD=""
    #COUNT_FIELD="receivedate"
    #COUNT_FIELD="patient.drug.drugindication.exact"
    fields["COUNT_FIELD"] = COUNT_FIELD

    SKIP_NUM_REC=skip
    fields["SKIP_NUM_REC"]=SKIP_NUM_REC

    LIMIT_REC=limit # default is 1; max value is 99
    fields["LIMIT_REC"]=LIMIT_REC

    template = Template('https://api.fda.gov/drug/event.json?api_key=$API_KEY&search=$SEARCH_TERMS&sort=$SORT_FIELD&limit=$LIMIT_REC&skip=$SKIP_NUM_REC&count=$COUNT_FIELD')
    #template = Template('https://api.fda.gov/drug/event.json?api_key=$API_KEY&limit=1')

    URL = template.substitute(**fields)

    data = requests.get(URL).json()
    try:
        total_recs = data["meta"]["results"]["total"]
        num_recs_returned = len(data["results"])
    except KeyError:
        print(data)
        return None
    if find_all is False:
        print(URL)
        print("Total records: ", total_recs)
        print("Returned records: ", num_recs_returned)
        return data
    
    # use paging 
    meta = data["meta"]
    # results = data["results"]
    results = []
    found_recs = 0 # num_recs_returned
    
    first_run = True
    page_size = 99 # maximum value
    fields["LIMIT_REC"]= page_size 
    while found_recs+skip < total_recs:
        # NOTE: we keep the user-passed in 'skip' value
        # .. so if there 300 records, and skip=50, it will returns 250
        template = Template('https://api.fda.gov/drug/event.json?api_key=$API_KEY&search=$SEARCH_TERMS&sort=$SORT_FIELD&limit=$LIMIT_REC&skip=$SKIP_NUM_REC&count=$COUNT_FIELD')
    
        URL = template.substitute(**fields)
        print(URL)
        data = requests.get(URL).json()
        if "error" in data:
            print(data["error"])
            break
        print(data['meta']['results'])
        #total_recs = data["meta"]["results"]["total"]
        num_recs_returned = len(data["results"])
        found_recs += num_recs_returned
        print("Returned records so far: ", found_recs)
        fields["SKIP_NUM_REC"] += fields["LIMIT_REC"]
        print(type(data["results"]))
        results.extend(data["results"])
        
    meta["results"]["limit"] = len(results)
    data = {"meta": meta, "results": results}
    pp.pprint(meta)
    print("Total records: ", len(results))
    #data = requests.get(URL).json()
    """
    "meta": {
       "results": {
          "skip": 0,
          "limit": 2,
          "total": 9911880
        }
    }
    """
    return data