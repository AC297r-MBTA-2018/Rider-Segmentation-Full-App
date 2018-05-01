/*
 * ClusterDonutChart - Object constructor function
 * @param _parentElement 	        -- the HTML element in which to draw the visualization
 * @param _data			          	-- the actual data
 * @param _clusterSelection			-- cluster selection
 * @param _titleText                -- chart title
 * @param _colors                   -- color scale
 */

ClusterDonutChart = function(_parentElement, _data, _titleText, _colors) {
    this.parentElement = _parentElement;
    this.data = _data;
    this.titleText = _titleText;
    this.colors = _colors;
    this.$graphicContainer = $("#" + _parentElement);

    this.initVis();
}

ClusterDonutChart.prototype.initVis = function() {
    var vis = this;

    vis.margin = {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
    };

    if ($("#" + vis.parentElement).width() - vis.margin.right - vis.margin.left > 200) {
        vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    } else {
        vis.width = 200;
    }
    vis.height = 400 - vis.margin.top - vis.margin.bottom;
    vis.wrangleData();
}

ClusterDonutChart.prototype.wrangleData = function() {
    var vis = this;
    vis.displayData = vis.data;
    vis.updateVis();
}

ClusterDonutChart.prototype.updateVis = function() {
    var vis = this;
    vis.pie = new d3pie(vis.parentElement, {
        "size": {
            "canvasHeight": vis.height,
            "canvasWidth": vis.width,
            "pieInnerRadius": "60%",
            "pieOuterRadius": "70%"
        },
        "header": {
            "title": {
                "text": vis.titleText
            },
            "location": "pie-center",
        },
        "data": {
            "sortOrder": "label-desc",
            "smallSegmentGrouping": {
                "enabled": true
            },
            "content": vis.displayData
        },
        "labels": {
            "outer": {
                "format": "label-percentage2",
                "pieDistance": 20
            },
            "inner": {
                "format": "none"
            },
            "mainLabel": {
                "fontSize": 11
            },
            "percentage": {
                "color": "#999999",
                "fontSize": 11,
                "decimalPlaces": 2
            },
            "value": {
                "color": "#cccc43",
                "fontSize": 11
            },
            "lines": {
                "enabled": true,
                "color": "#777777"
            },
            "truncation": {
                "enabled": true
            }
        },
        "tooltips": {
            "enabled": true,
            "type": "placeholder",
            "string": "{label}: {percentage}%",
            "styles": {
                "backgroundOpacity": 0.7,
                "borderRadius": 3,
                "fontSize": 11
            }
        },
        "misc": {
            "colors": {
                segments: vis.colors
            },
            "canvasPadding": {
                "top": 20,
                "right": 20,
                "bottom": 20,
                "left": 20
            },
        }
    })
}
