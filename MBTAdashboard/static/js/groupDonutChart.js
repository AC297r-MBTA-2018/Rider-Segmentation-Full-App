/*
 * GroupDonutChart - Object constructor function
 * @param _parentElement 	        -- the HTML element in which to draw the visualization
 * @param _selectorParentElement 	-- the HTML element in which to draw the cluster selector
 * @param _data			          	-- array of data, element = data for 1 donut chart
 * @param _titleTexts               -- chart titles
 * @param _nGraphPerRow             -- number of Donur charts per row (2, 3, or 4 typically)
 * @param _clusterSelection			-- cluster selection
 * @param _colors                   -- range of colors for color scale
 * @param _view                     -- whether viewing by cluster
 */

GroupDonutChart = function(_parentElement, _selectorParentElement, _data, _titleTexts, _nGraphPerRow, _clusterSelection, _colors, _view = false) {
    this.parentElement = _parentElement;
    this.selectorParentElement = _selectorParentElement;
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

GroupDonutChart.prototype.initVis = function() {
    var vis = this;
    // console.log(vis.data);
    // console.log(vis.nCluster);

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

    // intialize with one radio button default view of overall
    vis.appendDataSelector();

    // Appened one HTML element for each donut Chart
    vis.appenedDonutDivs();

    vis.wrangleData();

    // Listen to view change events
    // If view is overall, append one radio button with value = Overall
    if (vis.view) { // if view by_cluster
        $('#' + vis.selectorParentElement + ' div input').click(function() {
            vis.clusterSelection = d3.select(this).property("value");
            vis.wrangleData();
        });
    };
}

GroupDonutChart.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data.map(function(d) {
        return d[vis.clusterSelection];
    })
    vis.updateVis();
}

GroupDonutChart.prototype.updateVis = function() {
    var vis = this;

    // draw a donut chart for each item in vis.displayData
    vis.displayData.forEach(function(d, i) {
        var newParentElement = vis.prefix + '_' + i;
        $('#' + newParentElement).empty();
        var donutChart = new ClusterDonutChart(newParentElement, d, vis.titleTexts[i], vis.colors);
    });
}

GroupDonutChart.prototype.appenedDonutDivs = function() {
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

// Helper function to append cluster selector options
GroupDonutChart.prototype.appendDataSelector = function() {
    var vis = this;

    $("#" + vis.selectorParentElement).empty(); // clear out the selection div
    var p = document.getElementById(vis.selectorParentElement);

    // append selector
    if (vis.view) { // view by_cluster
        var html_str = '<form class="form-inline" role="group" id="' + vis.selectorPrefix + '-cluster-selector">' +
        '<label class="form-label p-2" for="' + vis.selectorPrefix + '-cluster-selector">View cluster: </label>' +
            '<div class="form-check">' +
            '<input class="form-check-input" name="clusterview" type="radio" id="' + vis.selectorPrefix + '-cluster-0" value="0" checked="checked"' +
            '<label class="form-check-label" for="' + vis.selectorPrefix + '-cluster-0"> 0 </label>' +
            '</div>';

        // append a radio button for each cluster
        for (var i = 1; i < vis.nCluster; i++) {
            var selectsionsHTML = '<div class="form-check ml-2 mr-2">' +
                '<input class="form-check-input" name="clusterview" type="radio" id="' + vis.selectorPrefix + '-cluter-' + i + '" value= "' + i + '"' +
                '<label class="form-checl-label" for="' + vis.selectorPrefix + '-clusterview"> ' + i + ' </label>' +
                '</div>'
            html_str += selectsionsHTML;
        }
        html_str += '</form>';
        p.innerHTML = html_str;

    } else { // view overview
        p.innerHTML = '<form class="form-inline ml-2 mr-2" role="group" id="' + vis.selectorPrefix + '-cluster-selector">' +
            '<label class="form-label p-2" for="' + vis.selectorPrefix + '-cluster-selector">View: </label>' +
            '<div class="form-check">' +
            '<input class="form-check-input" name="overview" type="radio" id="' + vis.selectorPrefix + '-overview" checked="checked"' +
            '<label class="form-check-label" for="' + vis.selectorPrefix + '-overview"> Overview </label>' +
            '</div></form>';
    }
}
