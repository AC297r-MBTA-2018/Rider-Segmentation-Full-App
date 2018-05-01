/*
 *  StationMap - Object constructor function
 *  @param _parentElement   	-- HTML element in which to draw the visualization
 *  @param _data            	-- Array with all stations of the bike-sharing network
 *  @param _clusterSelection  -- Cluster number to visualize
 */

BostonMap = function(_parentElement, _data, _clusterSelection, _colors, _view=false) {

	this.parentElement = _parentElement;
	this.data = _data;
	this.clusterSelection = _clusterSelection;
	this.colors = _colors;
	this.view = _view; // false = overview; true = by_cluster

	this.valueMax = d3.max(_data.map(function(d){
			return d3.max(d, function (e) { return e.properties.value; });
	}));

	this.valueMin = d3.min(_data.map(function(d){
			return d3.min(d, function (e) { return e.properties.value; });
	}));

	this.buckets = _colors.length;;
	this.valueScale = d3.range(this.valueMin, this.valueMax, this.valueMax/this.buckets);

	this.initVis();
}


/*
 *  Initialize station map
 */

BostonMap.prototype.initVis = function() {
	var vis = this;
	// intialize with one radio button default view of overall
	vis.appendDataSelector();

	vis.bostonMap = L.map(vis.parentElement).setView([42.360082, -71.058880], 11);

    // L.Icon.Default.imagePath = 'img/';
		vis.mapGridLayerGroup = L.layerGroup().addTo(vis.bostonMap);
    L.tileLayer('http://{s}.tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'})
        .addTo(vis.mapGridLayerGroup);

    $.getJSON("/load_MBTA_geoJSON", function(geoJSONdata) {
      vis.mbtaLinesLayerGroup = L.layerGroup().addTo(vis.bostonMap);
			L.geoJson(geoJSONdata.features, {
          style: styleMBTAlines,
          weight: 10
      }).addTo(vis.mbtaLinesLayerGroup);

      function styleMBTAlines(feature){
          var lineColor = feature.properties.LINE;
          return {color: lineColor.toLowerCase(),
									opacity: 0.45};
      }
    });

		// Add cluster zipcode pattern layer group
		vis.zipCodeLayerGroup = L.layerGroup().addTo(vis.bostonMap);

		vis.wrangleData();

		// Listen to view change events
		// If view is overall, append one radio button with value = Overall
		if (vis.view) { // if view by_cluster
			$('#geo-data-selection div input').click(function(){
				vis.clusterSelection = d3.select(this).property("value");
				vis.zipCodeLayerGroup.clearLayers(); // clear previous layers to redraw
				vis.wrangleData();
			})
		}
}


/*
 *  Data wrangling
 */

BostonMap.prototype.wrangleData = function() {
	var vis = this;
	// filter data based on selection
	vis.displayData = vis.data[vis.clusterSelection];

	// Update the visualization
	vis.updateVis();
}


/*
 *  The drawing function
 */
BostonMap.prototype.updateVis = function() {
	var vis = this;

	L.geoJson(vis.displayData, {style: styleZipCode}).addTo(vis.zipCodeLayerGroup);

	function getColor(d) {
		return 	d < vis.valueScale[0] ? vis.colors[0] :
						d < vis.valueScale[1] ? vis.colors[1] :
						d < vis.valueScale[2] ? vis.colors[2] :
						d < vis.valueScale[3] ? vis.colors[3] :
						d < vis.valueScale[4] ? vis.colors[4] :
						d < vis.valueScale[5] ? vis.colors[5] :
						d < vis.valueScale[6] ? vis.colors[6] :
						d < vis.valueScale[7] ? vis.colors[7] :
																		vis.colors[8];
	}

	//
	function styleZipCode(feature){
		return {
			weight: 2,
      opacity: 0.8,
			color: "white",
			dashArray: '3',
			fillColor: getColor(feature.properties.value),
			fillOpacity: 0.6
		};
	}

}


// Helper function to append cluster selector options
BostonMap.prototype.appendDataSelector = function() {
	var vis = this;
	$("#geo-data-selection").empty(); // clear out the selection div
	var p = document.getElementById("geo-data-selection");
	// reappend selector
	if (vis.view){ // view by_cluster
	 	var html_str = '<form class="form-inline ml-2 mr-2" role="group" id="geo-cluster-selector">' +
		'<label class="form-label p-2" for="geo-cluster-selector">View cluster: </label>' +
				'<div class="form-check">' +
				'<input class="form-check-input" name="overview" type="radio" id="geo-cluster-0" value="0" checked="checked"' +
				'<label class="form-check-label" for="geo-cluster-0"> 0 </label>' +
				'</div>';

		// append a radio button for each cluster
		for (var i = 1; i < vis.data.length; i++){
			var newSelectsionsHTML = '<div class="form-check ml-2 mr-2">' +
			'<input class="form-check-input" name="overview" type="radio" id="geo-cluter_' + i + '" value= "' + i + '"' +
			'<label class="form-checl-label" for="geo-overview">' + i + ' </label>' +
			'</div>'
			html_str += newSelectsionsHTML;
		}
		html_str += '</form>';
		p.innerHTML = html_str;

	}
	else { // view overview
		p.innerHTML = '<form class="form-inline ml-2 mr-2" role="group" id="geo-cluster-selector">' +
		'<label class="form-label p-2" for="geo-cluster-selector">View: </label>' +
				'<div class="form-check">' +
				'<input class="form-check-input" name="overview" type="radio" id="geo-overview" checked="checked"' +
				'<label class="form-check-label" for="geo-overview"> Overview </label>' +
				'</div></form>';
	}
}
