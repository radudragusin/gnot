import re
from db import export_sql
from jinja2 import Markup

def render(vis, request, info):
	info["message"] = [] 
	table = request.args.get("table", '')
	xField = request.args.get("xField", '')
	field = request.args.get("field", '') 
	where = request.args.get("where", '1=1')
	limit = request.args.get("limit", '3650') # 10 years max
	start = request.args.get("start", '0') # start at 0
		
	reload = int(request.args.get("reload", 0))
	view = request.args.get("view", '')

	if len(table) == 0 or len(xField) == 0:
		info["message"].append("Table or xField missing")
		info["message_class"] = "failure"
	else:
		sql = "select %s, %s from %s where %s group by 1 order by 1 limit %s offset %s"%(xField, field, table, where,limit, start)

		header =  "Date,Field"
		
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

	field = ','.join([re.compile(r'as').split(f)[-1].strip() for f in field.split(',')])
	info["message"] = Markup(''.join('<p>%s</p>'%m for m in info["message"] if len(m) > 0))
	info["title"] = "%s from %s"%(field, table)
	info['query']= Markup(request.args.get('query', ''))
	

	