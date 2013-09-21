import os,re
import json, csv
from jinja2 import Markup
from db import export_sql
def render(vis, request, info):
	info["message"] = []
	
	reload = request.args.get("reload", 0)
	table = request.args.get("table", '')
	where = request.args.get("where", '1=1')
	field = request.args.get("field", '')
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	limit = request.args.get("limit", '1000')
	groupby = field
	
	if len(table) == 0 or len(field) == 0:
		info["message"].append("table or field missing.")
		info["message_class"] = "failure"
	else:
		sql = "select %s, count(*) as n from %s where %s group by %s order by 2 desc limit %s offset %s"%(field, table, where, groupby, limit, start)

		(datfile, reload, result) = export_sql(sql, vis.config, reload, None, view)
		if len(result) > 0:
			info["message"].append(result)
			info["message_class"] = "failure"
		else:
			info["message_class"] = "success"
			if reload > 0:
				info["message"].append("Loaded fresh.")
			else:
				info["message"].append("Loading from cache. Use reload=1 to reload.")
			
			info["datfile"] = datfile
		
		
		json_file = datfile.replace('csv', 'json')	
		if reload > 0 or (not os.path.exists(os.path.realpath(json_file))):
			#csv to json conversion
			try:
				reader = csv.DictReader(open(datfile, 'r'), fieldnames = ( "name","size" ) )
				out = [obj for obj in reader if  len(obj['name']) > 0]
				with open(json_file, 'w') as jf:
					json.dump({"name":'flare',"children":out}, jf)
			except:
				info["message"].append("Couldn't find CSV file")
				info["message_class"] = "failure"
			
		info["message_class"] = "success"
		info["datfile"] = json_file
	
	field = ','.join([re.compile(r'as').split(f)[-1].strip() for f in field.split(',')])
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
	info["title"] = "%s from %s"%(field, table)		