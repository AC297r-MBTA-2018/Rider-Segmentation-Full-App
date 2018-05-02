/*
 *  ClusterReport - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _selectorParentElement   -- HTML element in which to append data selector
 *  @param _data            -- array of data
 */

ClusterReport = function(_parentElement, _selectorParentElement, _data, _view=false) {
    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.selectorParentElement = _selectorParentElement
    this.data = _data;
    this.nCluster = _data.length;
    this.view = _view;
    this.selectorPrefix = 'report';
    this.clusterSelection = 0;
    this.duration = 1000;

    this.initVis();
}
/*
 * Initialize visualization (static content, e.g. SVG area or axes)
 */
ClusterReport.prototype.initVis = function() {
    var vis = this;

    // intialize with one radio button default view of overall
    vis.appendDataSelector();

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


ClusterReport.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data[vis.clusterSelection];
    vis.updateVis();
}

ClusterReport.prototype.updateVis = function() {
    var vis = this;

    $("#" + vis.parentElement).empty(); // clear out the div
    var p = document.getElementById(vis.parentElement);

    var html_str = '<p class="text-justify">' + vis.displayData + '</p>'
    p.innerHTML = html_str;
}

ClusterReport.prototype.appendDataSelector = function() {
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
