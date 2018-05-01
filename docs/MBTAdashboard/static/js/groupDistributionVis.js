/*
 * GroupDistributionChart - Object constructor function
 * @param _parentElement 	        -- the HTML element in which to draw the visualization
 * @param _selectorParentElement 	-- the HTML element in which to draw the cluster selector
 * @param _data			          	-- array of data, element = data for 1 chart
 * @param _titleTexts               -- chart titles
 * @param _nGraphPerRow             -- number of Donur charts per row (2, 3, or 4 typically)
 * @param _clusterSelection			-- cluster selection
 * @param _colors                   -- range of colors for color scale
 * @param _view                     -- whether viewing by cluster
 */
 GroupDistributionChart = function(_parentElement, _selectorParentElement, _selectorChildElement, _data, _titleTexts, _nGraphPerRow, _clusterSelection, _colors, _view = false) {
     this.parentElement = _parentElement;
     this.selectorParentElement = _selectorParentElement;
     this.selectorChildElement = _selectorChildElement;
     this.data = _data; // an array of data each item is one donut chart
     this.titleTexts = _titleTexts; // an array of string for each donut chart
     this.nGraphPerRow = _nGraphPerRow;
     this.clusterSelection = _clusterSelection;
     this.colors = _colors;
     this.view = _view; // false = overview; true = by_cluster
     this.nGraph = _data.length;
     this.nCluster = _data[0].length;
     this.prefix = _parentElement.split("-")[0];
     this.selectorPrefix = _selectorParentElement.split("-")[0];
     this.$graphicContainer = $("#" + _parentElement);

     this.initVis();
 }

 GroupDistributionChart.prototype.initVis = function() {
     var vis = this;

     vis.appendChartTypeSelector();
     // default view is donut chart
     vis.selection = "donut";

     vis.wrangleData();

     // listen to selection changes
     $('#' + vis.selectorParentElement + ' div input').click(function() {
         vis.selection = d3.select(this).property("value");
         vis.wrangleData();
     });
 }

 GroupDistributionChart.prototype.wrangleData = function() {
     var vis = this;
     // if donut chart, wrangle data into 'label': key, 'value': value form
     if (vis.selection == "donut"){
         vis.displayData = vis.processData();
     }
     else {
         // no need to process data for stacked chart
         vis.displayData = vis.data;
     }
     vis.updateVis();
 }
 // drawing function
 GroupDistributionChart.prototype.updateVis = function() {
     var vis = this;
     // console.log(vis.displayData);
     var count = vis.displayData.map(function(d){
         var sum =0;
         for (i in d){
             for (j in d[i]){
                 sum += d[i][j].value;
             }
         }
         return sum;
     });
     if (vis.selection == "donut"){
         var groupDistributionVis = new GroupDonutChart(vis.parentElement, vis.selectorChildElement, vis.displayData, vis.titleTexts, vis.nGraphPerRow, vis.clusterSelection, vis.colors, vis.view);
     }
     else {
         var groupDistributionVis = new MultiStackedBarChart(vis.parentElement, vis.selectorChildElement, vis.displayData, vis.titleTexts, vis.nGraphPerRow, vis.colors, vis.view);
     }
 }

GroupDistributionChart.prototype.appendChartTypeSelector = function() {
    var vis = this;

    $("#" + vis.selectorParentElement).empty(); // clear out the selection div
    var p = document.getElementById(vis.selectorParentElement);

    // append selector
    var html_str =
        '<form class="form-inline" role="group" id="' + vis.selectorPrefix + '-charttype-selector">' +
        '<label class="form-label p-2" for="' + vis.selectorPrefix + '-charttype-selector">Chart type: </label>' +
        '<div class="form-check">' +
        '<input class="form-check-input" name="mode" type="radio" id="' + vis.selectorPrefix + '-donut-chart" value="donut" checked="checked"' +
        '<label class="form-check-label" for="' + vis.selectorPrefix + '-donut-chart"> Donut Chart </label>' +
        '</div>' +
        '<div class="form-check">' +
        '<input class="form-check-input ml-2" name="mode" type="radio" id="' + vis.selectorPrefix + '-stacked-chart" value="stackedbar"' +
        '<label class="form-check-label" for="' + vis.selectorPrefix + '-stacked-chart"> Stacked Bar Chart </label>' +
        '</div>';
    html_str += '</form>';
    p.innerHTML = html_str;
}

 // Function to turn key: value pairs into 'label': key, 'value': value
 // Function for donut chart and regular bar chart
 GroupDistributionChart.prototype.processData = function() {
     var vis = this;
     var fullProcessedData = [];

     vis.data.forEach(function(cluster){
         var processedData = []; // for cluster i
         cluster.forEach(function(item){
             var newObjList = [];
             for (i in item){
                 newObj = {};
                 newObj["label"] = i;
                 newObj["value"] = item[i];
                 newObjList.push(newObj);
             };
             processedData.push(newObjList);
         });
         fullProcessedData.push(processedData);
     });
     return fullProcessedData
 }
