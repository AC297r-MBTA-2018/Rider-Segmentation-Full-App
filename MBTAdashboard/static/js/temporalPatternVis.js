/*
 *  TemporalPatternChart - Object constructor function
 *  @param _parentElement   -- HTML element in which to draw the visualization
 *  @param _data            -- array of data
 *  @param _colors          -- array of colors
 *  @param _nGraph          -- number of graphs to compare
 *  @param _showLegend          -- whether to show legend
 */

TemporalPatternChart = function(_parentElement, _data, _titleList, _nGraph, _colors, _showLegend = true) {
    this.nGraph = _nGraph;
    this.titleList = _titleList;
    this.nGraphPerSlide = 6;
    this.nCarouselSlide = 0;
    this.$graphicContainer = $("#" + _parentElement);
    this.parentElement = _parentElement;
    this.data = _data;
    this.colors = _colors;
    this.duration = 1000;
    this.maxSaturation = d3.max(this.data.map(function(d) {
        return d3.max(d, function(e) {
            return e.value;
        });
    }));
    this.showLegend = _showLegend;
    this.initVis();
}

/*
 * Initialize visualization (static content, e.g. SVG area or axes)
 */
TemporalPatternChart.prototype.initVis = function() {
    var vis = this;
    vis.margin = {
        top: 50,
        right: 30,
        bottom: 5,
        left: 30
    };
    vis.legendElementWidth = Math.floor(vis.width / 24);

    if ($("#" + vis.parentElement).width() - vis.margin.right - vis.margin.left > 200) {
        vis.width = $("#" + vis.parentElement).width() - vis.margin.left - vis.margin.right;
    } else {
        vis.width = 500;
    }
    vis.height = 500 - vis.margin.top - vis.margin.bottom;

    document.getElementById(vis.parentElement)
        .setAttribute("style", "height: " + vis.height + ";");

    vis.wrangleData();
}

TemporalPatternChart.prototype.wrangleData = function() {
    var vis = this;
    vis.updateVis();
}

TemporalPatternChart.prototype.updateVis = function() {
    var vis = this;
    var p = document.getElementById(vis.parentElement);


    if (vis.nGraph === 1) {
        htmlStr = '<div class="row">\n';
        htmlStr += '<div class="col-sm-12 reduced-padding">' +
            '<div id="heatmap' + 0 + '_carousel' + 0 + '"></div></div>';
        htmlStr += '</div>';
        p.innerHTML = htmlStr;
    } else if (vis.nGraph <= vis.nGraphPerSlide) {
        htmlStr = '<div class="row">\n';
        for (i = 0; i < vis.nGraph; i++) {
            htmlStr += '<div class="col-sm-6 reduced-padding">' +
                '<div id="heatmap' + i + '_carousel' + 0 + '"></div></div>';
        }
        htmlStr += '</div>';
        p.innerHTML = htmlStr;
    } else {
        vis.nCarouselSlide = Math.ceil(vis.nGraph / vis.nGraphPerSlide);
        carouselHtmlStr = '<div id="timePatternCarousel" class="carousel slide" data-ride="carousel" data-pause=true>\n' +
            '<div class="carousel-inner">';
        carouselCtrlHtmlStr = '<a class="carousel-control-prev" href="#timePatternCarousel" role="button" data-slide="prev">' +
            '<i class="fa fa-chevron-left"></i>' +
            '<span class="sr-only">Previous</span>' +
            '</a>' +
            ' <a class="carousel-control-next" href="#timePatternCarousel" role="button" data-slide="next">' +
            '<i class="fa fa-chevron-right"></i>' +
            '<span class="sr-only">Next</span>' +
            '</a>' +
            '</div>';
        var numGraph = 0;
        for (j = 0; j < vis.nCarouselSlide; j++) {
            if (j === 0) {
                carouselHtmlStr += '<div class="carousel-item active">';
            } else {
                carouselHtmlStr += '<div class="carousel-item">';
            }
            // add heatmaps to each slide
            htmlStr = '<div class="container">\n<div class="row">\n';
            for (i = 0; i < vis.nGraphPerSlide; i++) {
                if (numGraph < vis.nGraph) {
                    htmlStr += '<div class="col-sm-6 reduced-padding">' +
                        '<div id="heatmap' + i + '_carousel' + j + '"></div></div>';
                    numGraph += 1;
                }
            }
            htmlStr += '</div></div>';
            carouselHtmlStr += htmlStr + '</div>';

        }
        carouselHtmlStr += '</div>' + carouselCtrlHtmlStr;
        p.innerHTML = carouselHtmlStr;

    }

    vis.drawHeatmaps();
}

TemporalPatternChart.prototype.drawHeatmaps = function() {
    var vis = this;
    var numDrawnGraph = 0;
    if (vis.nCarouselSlide === 0) {
        for (i = 0; i < vis.nGraphPerSlide; i++) {
            if (numDrawnGraph < vis.nGraph) {
                var heatmapVis = new HourlyHeatmap("heatmap" + i + "_carousel" + 0, vis.data[numDrawnGraph], vis.titleList[numDrawnGraph], vis.colors, vis.maxSaturation, vis.showLegend);
                numDrawnGraph += 1;
            }
        }
    } else {
        for (j = 0; j < vis.nCarouselSlide; j++) {
            for (i = 0; i < vis.nGraphPerSlide; i++) {
                if (numDrawnGraph < vis.nGraph) {
                    var heatmapVis = new HourlyHeatmap("heatmap" + i + "_carousel" + j, vis.data[numDrawnGraph], vis.titleList[numDrawnGraph], vis.colors, vis.maxSaturation, vis.showLegend);
                    numDrawnGraph += 1;
                }
            }
        }
    }
}
