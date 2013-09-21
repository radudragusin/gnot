/*!
 * Load Search Box
 */

jQuery.noConflict();
 
(function( $ ) {

	function getKeys(obj) {
	  var name, result = [];
	
	  for (name in obj) {
	    if (obj.hasOwnProperty(name)) {
	      result[result.length] = name;
	    }
	  }
	  return result;
	}


	var uri = parseUri(document.location.search);
	 
	var query = uri.queryKey['query'];
	 if(typeof query != 'undefined') 
	 	query = decodeURIComponent(query).replace(/\+/g, ' ');
	 else
	 	query = '';
	 
	 
	$("#form_module_tables").submit(function() {
		$('#query-input').val(window.visualSearch.searchBox.value());
		return true;
	});
	
	Array.prototype.diff = function(a) {
		    return this.filter(function(i) {return !(a.indexOf(i) > -1);});
		};
	
	  d3.json("render?query=module%3A+explore_db", function(error, data) {
	    window.visualSearch = VS.init({
	      container  : $('#search_box_container'),
	      query      : query,
	      showFacets : true,
	      unquotable : [
	        'module',
	        'table',
	        'reload',
	        'start',
	        'limit'
	      ],
		  placeholder : "Make your choices ... ",
	      callbacks  : {
	        search : function(query, searchCollection) {
	          var $query = $('#search_query');
			  
			  $query.stop().animate({opacity : 1}, {duration: 300, queue: false});
	          $query.html('<span class="raquo">&raquo;</span> Your query is: <b>' + searchCollection.serialize() + '</b>');
	          clearTimeout(window.queryHideDelay);
	          window.queryHideDelay = setTimeout(function() {
	            $query.animate({
	              opacity : 0
	            }, {
	              duration: 30000,
	              queue: false
	            });
	          }, 2000);
	        },
	        valueMatches : function(category, searchTerm, callback) {
	        	  var sq = window.visualSearch.searchBox.app.searchQuery.facets();
		          switch (category) {
					case 'module':
						callback(getKeys(data['modules']));
						break;
					case 'table':
						callback(getKeys(data['tables']));
						break;
					case 'reload':
						callback(['0', '1']);
						break;

					default:			
						var module = 0;
						sq.forEach(function (d) { if('module' in d) module = d['module'] });
						
						var value = 0;
						if (module && module in data['modules'] && category in data['modules'][module] && data['modules'][module][category])
							value = data['modules'][module][category]['values'];

						if (value instanceof Array){
							callback(value);
							break;
						}
						else if (value === "fields"){
							// fall through
						}
						else {
							break;
						}

					case 'field':
						var table = 0;
						sq.forEach(function (d) { if('table' in d) table = d['table'] });
						var fields = [];
						if  (table && table in data['tables']) fields = data['tables'][table]
						callback(fields);
						break;
		          }
	        },
	        facetMatches : function(callback) {
	        	var sq = window.visualSearch.searchBox.app.searchQuery.facets();
				var module = 0; sq.forEach(function (d) { if('module' in d) module = d['module']; });
				
				var options = ['module', 'table', 'field', 'where', 'start', 'limit', 'reload', 'view']; 
				var uniqueOptions = ['module', 'table', 'field', 'where', 'start', 'limit', 'reload', 'view'];
				
				if (module) {
					var moduleOptions = getKeys(data['modules'][module]);
					for (var i = 0; i < moduleOptions.length; i++) {
						options.push(moduleOptions[i]);
						if (data['modules'][module][moduleOptions[i]]['n'] == 1) {
							uniqueOptions.push(moduleOptions[i]);
						}
						
					}
				}
				
				var rOptions = [];
				for (var i=0; i<options.length; i++) {
					if ($.inArray(options[i], uniqueOptions) >= 0) {
						var present = 0; sq.forEach(function (d) { if(options[i] in d) present=1; });
						if (!present) {
							rOptions.push(options[i]);
						}
					}
					else{
						rOptions.push(options[i]);
					}
				}
				callback(rOptions,{preserveOrder: true});
	        }
	      }
	    });
	  });
})( jQuery );
 