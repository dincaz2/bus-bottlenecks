import * as L from "leaflet";
import 'jquery';
import 'leaflet-providers';
import * as d3fetch from "d3-fetch";
import * as leaflet_grp_lyr from "leaflet-groupedlayercontrol";
import * as SQL from "sql.js";
import * as d3color from "d3-color"
import * as d3scale from "d3-scale"
import * as d3scalechrom from "d3-scale-chromatic"
import textures from 'textures';
import moment from "moment";
import 'jquery-datetimepicker';


/** Map generation section**/
var map;
var heatMapLayerId;
var starting_point_marker;
var default_starting_location = [32.087429, 34.849112];
var starting_location;
var default_starting_zoom = 15;
var goToHeatLayerButtonDiv;
var controlLayer;
var date_time_picker;

//Creating the grey icon
var geryIcon = new L.Icon({
    iconUrl: 'assets/images/marker-icon-grey.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});


function createMap() {
    map = L.map('map', {renderer: new L.canvas()})
        .setView([32.070748, 34.775320], default_starting_zoom)


    var tileLayers = makeTileLayers();
    tileLayers[getDefaultLayerName()].addTo(map);
    controlLayer = L.control.layers(tileLayers).addTo(map);

    //Add scale
    L.control.scale().addTo(map);

    //Fixing the grey tiles partial issue
    $(window).on("resize", function () { $("#map").height($(window).height()); map.invalidateSize(); }).trigger("resize");

    // setting for default path of images used by leaflet - otherwise marker only appear after first click
    delete L.Icon.Default.prototype._getIconUrl;

    L.Icon.Default.mergeOptions({
        iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
        iconUrl: require('leaflet/dist/images/marker-icon.png'),
        shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
    });

    return map;
}


function getDefaultLayerName() {
    return 'Stamen Toner Light';
};

function makeTileLayers() {
    return {
        'Stamen Toner Light':
            L.tileLayer.provider('Stamen.TonerLite', {
                attribution: 'Map tiles by <a href="http://stamen.com">Stamen Design</a>,' +
                    ' <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map data &copy;' +
                    ' <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' +
                    '<br>' +
                    'Transit data provided by <a href="http://miu.org.il/">Merhav</a>'
            }),
        'OpenStreetMap Mapnik':
            L.tileLayer.provider('OpenStreetMap.Mapnik', {
                attribution: 'Map tiles & data  &copy;' +
                    ' <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' +
                    '<br>' +
                    'Transit data provided by <a href="http://miu.org.il/">Merhav</a>' +
                    ' and processed by <a href="https://github.com/CanalTP/navitia">Navitia</a> '
            }),
        'OpenStreetMap BlackAndWhite':
            L.tileLayer.provider('OpenStreetMap.BlackAndWhite', {
                attribution: 'Map tiles & data  &copy;' +
                    ' <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' +
                    '<br>' +
                    'Transit data provided by <a href="http://miu.org.il/">Merhav</a>' +
                    ' and processed by <a href="https://github.com/CanalTP/navitia">Navitia</a> '
            }),
    };
}


function addLegend(line_colors) {
    var legend = L.control({position: 'bottomright'});

    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'info legend'),
            // grades = [0, 10, 20, 50, 100, 200, 500, 1000],
            labels = [];

        // loop through our density intervals and generate a label with a colored square for each interval
        for (var i = 0; i < line_colors.length; i++) {
            div.innerHTML +=
                '<i style="background:' + getColor(line_colors[i] + 1) + '"></i> ' +
                line_colors[i] + (line_colors[i + 1] ? '&ndash;' + line_colors[i + 1] + '<br>' : '+');
        }

        return div;
    };

    legend.addTo(map);
}


function get_list_of_routes() {
    // var promises = [];
    // var list_of_shape_files = [];
    // var file = 'assets/data/route_list.txt';
    // promises.push(d3fetch.text(file))
    //
    // Promise.all(promises).then(function (values) {
    //     values.forEach(function (data) {
    //         data.split(",").forEach(function(route) {
    //             route = route.replace(/\"/g,"")
    //             route = route.replace(/\n/g,"")
    //             list_of_shape_files.push(route)
    //         })
    //     });
    //     addPolyLineForLine(list_of_shape_files);
    // });
}

var minSpeed = 25
var maxSpeed = 0
var colors = d3scale.scaleQuantize()
    .domain([minSpeed,maxSpeed])
    .range(d3scalechrom.schemeReds[5]);

function style_segment(speed) {
    return  {
        "color": colors(speed),
        "weight": 10,
        "opacity": 1
    };

}

function style_segment_with_bus_extreme() {
    return  {
        "color": "yellow",
        "weight": 2,
        "opacity": 1
    };
}
function build_segments() {
    var promises = [];
    var list_of_shape_files = [];

    // var xhr = new XMLHttpRequest();
    // xhr.open('GET', '/path/to/database.sqlite', true);
    // xhr.responseType = 'arraybuffer';
    //
    // xhr.onload = function(e) {
    //     var uInt8Array = new Uint8Array(this.response);
    //     var db = new SQL.Database(uInt8Array);
    //     var segments_data= db.exec("SELECT * FROM segments" +
    //         "where day = '18/03/2019' and from = '08:30'");
    //     console.log(segments_data)
        //read the segments
        var file = 'assets/data/segments_data.json';
        promises.push(d3fetch.json(file))
        Promise.all(promises).then(function (values) {
            values = values[0]
            var re =  /\(.*?,.*?\)/gm;
            values.forEach(function (data) {
                var match;
                var coords = [];
                var lat, lon;
                while ((match = re.exec(data.Geometry)) != null) {
                    match = match[0]
                    match= match.split(/[\s(,)]+/)
                    var single_cord = [parseFloat(match[2]),parseFloat(match[1])]
                    coords.push(single_cord)
                }
                var geojson = {
                    "id": data.Segment,
                    "type": "LineString",
                    "coordinates": coords
                }

                var min = Math.ceil(minSpeed);
                var max = Math.floor(maxSpeed);
                var speed = Math.floor(Math.random() * (max - min + 1)) + min;

                var min = Math.ceil(0);
                var max = Math.floor(50);
                var num_of_buses = Math.floor(Math.random() * (max - min + 1)) + min;


                var segment_tooltip = "Avg. Speed: " + speed + " kph</br> #Buses: " + num_of_buses
                var segment_line = L.geoJSON(geojson, {
                        style: style_segment(speed, num_of_buses)
                    }
                ).bindTooltip(segment_tooltip)
                segment_line.addTo(map)

                if (num_of_buses > 20) {
                    var segment_line_exceeds_bus = L.geoJSON(geojson, {
                            style: style_segment_with_bus_extreme()
                        }
                    )
                    segment_line_exceeds_bus.addTo(map)
                }
            });
            date_time_picker = $('#datetimepicker').datetimepicker({
                formatDate: 'd.m.Y',
                formatTime: 'H:i',
                // default_Date: moment(navitia_service_start_date).format('DD.MM.YYYY'),
                minDate: moment("18.03.2019").format('DD.MM.YYYY'),
                maxDate: moment("23.03.2019").format('DD.MM.YYYY'),
                showSecond: false,
                step: 15,
            });

        });

    // };
    // xhr.send();


}

createMap();
build_segments();
