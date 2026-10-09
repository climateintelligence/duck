from duck.db import GraphDB
import pandas as pd
import json
import yaml


def display_image(base64_image):
    # img_data = base64.b64decode(base64_image)
    # img = Image.open(io.BytesIO(img_data))
    return '<img src="data:image/png;base64,{}" width="200"/>'.format(base64_image)


def display_json(data):
    content = yaml.dump(data, default_flow_style=True, indent=2)
    return f"<pre>{content}</pre>"


def query():
    query_str = """
        SELECT ?process ?dataset ?variable ?startTime ?endTime ?input ?output ?info ?histogram
        WHERE {
            ?exec rdf:type provone:Execution ;
                rdfs:label ?process ;
                clint:dataset_name ?dataset ;
                clint:variable_name ?variable ;
                prov:startedAtTime ?startTime ;
                prov:endedAtTime ?endTime ;
                clint:info ?info ;
                clint:histogram ?histogram .

            ?input rdf:type prov:Entity .

            ?output rdf:type prov:Entity ;
                prov:qualifiedDerivation [ prov:entity ?input; prov:hadActivity ?exec ] .
    }
    """  # noqa
    graph_db = GraphDB()
    results = graph_db.query(query_str)

    data = []
    for row in results:
        # print(row)
        process = row.process.split("/")[-1]
        dataset = row.dataset.value
        variable = row.variable.value
        start_time = row.startTime.value
        end_time = row.endTime.value
        input = row.input.split("/")[-1]
        input = input.split("urn:clint:")[-1]
        output = row.output.split("/")[-1]
        output = output.split("urn:clint:")[-1]
        # min = row.min.value
        # max = row.max.value
        # mean = row.mean.value
        # stddev = row.stddev.value
        info = json.loads(row.info.value)
        histogram = row.histogram.value
        entry = {
            "Process": process,
            "Dataset": dataset,
            "Variable": variable,
            "Start Time": start_time,
            "End Time": end_time,
            "Input": input,
            "Output": output,
            # "Min": min,
            # "Max": max,
            # "Mean": mean,
            # "StdDev": stddev,
            "Histogram": display_image(histogram),
        }
        for key in info:
            entry[key] = display_json(info[key])
        data.append(entry)
    df = pd.DataFrame(data)
    return df
