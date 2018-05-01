/*
 * MultiStackedBarChart - Object constructor function
 * @param _parentElement 	        -- the HTML element in which to draw the visualization
 * @param _selectorParentElement 	-- the HTML element in which to draw the view selector
 * @param _data			          	-- array of data, element = data for 1 stacked bar chart
 * @param _titleTexts               -- chart titles
 * @param _nGraphPerRow             -- number of Donur charts per row (2, 3, or 4 typically)
 * @param _colors                   -- range of colors for color scale
 * @param _view                     -- whether viewing by cluster
 */

 MultiStackedBarChart = function(_parentElement, _selectorParentElement, _data, _titleTexts, _nGraphPerRow, _colors, _view = false) {
     this.parentElement = _parentElement;
     this.selectorParentElement = _selectorParentElement;
     this.data = _data; // an array of data each item is one stacked chart
     this.titleTexts = _titleTexts; // an array of string for each stacked chart
     this.nGraphPerRow = _nGraphPerRow;
     this.colors = _colors;
     this.view = _view; // false = overview; true = by_cluster
     this.nGraph = _data.length;
     this.nCluster = _data[0].length;
     this.prefix = _parentElement.split("-")[0];
     this.selectorPrefix = _selectorParentElement.split("-")[0];
     this.$graphicContainer = $("#" + _parentElement);

     this.initVis();
 }

 MultiStackedBarChart.prototype.initVis = function() {
     var vis = this;

     vis.margin = {
         top: 0,
         right: 0,
         bottom: 0,
         left: 0
     };

     if ($("#" + vis.parentElement).width() - vis.margin.right - vis.margin.left > 500) {
         vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
     } else {
         vis.width = 500;
     }
     vis.height = 400 - vis.margin.top - vis.margin.bottom;

     // intialize view selector (stacked vs grouped)
     vis.appendViewSelector();

     // Appened one HTML element for each donut Chart
     vis.appenedStackedDivs();

     vis.wrangleData();
 }

 MultiStackedBarChart.prototype.wrangleData = function() {
     var vis = this;
     vis.displayData = vis.data;
     vis.updateVis();
 }

 MultiStackedBarChart.prototype.updateVis = function() {
     var vis = this;

     // draw a stacked chart for each item in vis.displayData
     vis.displayData.forEach(function(d, i) {
         var newParentElement = vis.prefix + '_' + i;
         $('#' + newParentElement).empty();
         var stackedChart = new StackedORGroupedBarChart(newParentElement, vis.selectorParentElement, d, vis.titleTexts[i], vis.colors, vis.view);
     });
 }

 MultiStackedBarChart.prototype.appenedStackedDivs = function() {
     var vis = this;

     var p = document.getElementById(vis.parentElement);

     htmlStr = '<div class="row">\n';
     for (i = 0; i < vis.nGraph; i++) {
         htmlStr += '<div class="col-sm-' + parseInt(12 / vis.nGraphPerRow) +
             ' p-0 m-0">' +
             '<div id="' + vis.prefix + '_' + i + '"></div></div>';
     }
     htmlStr += '</div>';

     p.innerHTML = htmlStr;
 }

 MultiStackedBarChart.prototype.appendViewSelector = function() {
     var vis = this;

     $("#" + vis.selectorParentElement).empty(); // clear out the selection div
     var p = document.getElementById(vis.selectorParentElement);

     // append selector
     var html_str =
         '<form class="form-inline" role="group" id="' + vis.selectorPrefix + '-barchart-selector">' +
         '<label class="form-label p-2" for="' + vis.selectorPrefix + '-barchart-selector">View type: </label>' +
         '<div class="form-check">' +
         '<input class="form-check-input" name="mode" type="radio" id="' + vis.selectorPrefix + '-stacked" value="stacked" checked="checked"' +
         '<label class="form-check-label" for="' + vis.selectorPrefix + '-stacked"> Stacked View </label>' +
         '</div>' +
         '<div class="form-check">' +
         '<input class="form-check-input ml-2" name="mode" type="radio" id="' + vis.selectorPrefix + '-grouped" value="grouped"' +
         '<label class="form-check-label" for="' + vis.selectorPrefix + '-grouped"> Grouped View </label>' +
         '</div>';
     html_str += '</form>';
     p.innerHTML = html_str;
 }
