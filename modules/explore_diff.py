import os
from db import export_sql
from jinja2 import Markup
import re
def render(vis, request, info):
	info["message"] = []
	table = request.args.get("table", '')
	field = request.args.get("field", '')
	where = request.args.get("where", '1=1')
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')
	start = request.args.get("start", '0') # start at 0
	limit = request.args.get("limit", '5000')#max 5000 data points
	
	xField = request.args.get("xField", '')
	
	splitfield = re.findall(r'[^,]*\([^\)]*\)[^,]*|[^,]+', field)
	
	if len(table) == 0 or len(xField) == 0 or len(field) == 0:
		info["message"].append("Table  or field missing.")
		info["message_class"] = "failure"
	elif  len(splitfield) < 2:
		info["message"].append("Need at least two fields.")
		info["message_class"] = "failure"
	else:
		sql = "select %s, %s from %s where %s group by 1 order by 1 limit %s offset %s"%(xField, field, table, where, limit, start)
		
		header =  "Date,A,B"
		
		(datfile, reload, result) = export_sql(sql, vis.config, reload, header, view)
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
	
	field = [re.compile(r'as').split(f)[-1].strip() for f in field.split(',')]
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))	
	field = 'diff of %s on %s'%(field[1], field[0])
	info["title"] = "%s from %s"%(field, table)