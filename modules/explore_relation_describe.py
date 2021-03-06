import os
import re
import json
import csv

from jinja2 import Markup

from db import export_sql


def nest_array(nlist, keys):
    k = keys.pop()
    jout = {}
    for row in nlist:
        rk = row[k]
        if not rk in jout:
            jout[rk] = []
        row['key'] = row[k]
        del row[k]
        jout[rk].append(row)
    joutN = []
    for rk in jout:
        if type(jout[rk]) == list:
            if len(keys) > 0:
                joutN.append({"key": rk, "_values": nest_array(jout[rk], keys[:])})
            else:
                joutN.append({"key": rk, "_values": jout[rk]})

    return joutN


def render(vis, request, info):
    info["message"] = []

    reload = int(request.args.get("reload", 0))

    sql = "select table_catalog, table_schema, table_name, column_name, data_type " \
          + "FROM information_schema.columns c left join pg_class p on c.table_name = p.relname " \
          + "where not (table_schema like '\%pg_\%' or table_schema like '\%gp\%' or table_schema like '\%schema\%') "

    (datfile, reload, result) = export_sql(sql, vis.config, reload, None, None, addHeader=True)
    json_file = datfile.replace('csv', 'json')

    if len(result) > 0:
        info["message"].append(result)
        info["message_class"] = "failure"
    else:
        info["message_class"] = "success"

        if reload > 0:
            info["message"].append("Loaded fresh.")

            keys = ['table_schema', 'table_name', 'column_name']
            keys.reverse()
            jout = nest_array(csv.DictReader(open(datfile)), keys)

            with open(json_file, 'w') as jf:
                json.dump([{'key':'DB', '_values': jout}], jf)

        else:
            info["message"].append("Loading from cache. Use reload=1 to reload.")


    info["datfile"] = json_file
    info["title"] = "DB CONTENT"
    info["title"] = Markup(info["title"])

    info["message"] = Markup(''.join('<p>%s</p>' % m for m in info["message"] if len(m) > 0))
