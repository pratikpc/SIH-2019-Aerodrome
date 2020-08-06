error_value = "No Obstacles found satisfying the given parameters";
function GetTextBoxValue(id) {
    return document.getElementById(id).value;
}

function GetTextBoxValues(format) {
    var icao = GetTextBoxValue('icao');
    var affected = GetTextBoxValue('affected');
    var obs_type = GetTextBoxValue('obs_type');
    var elevation = GetTextBoxValue('elevation');
    var latitude = GetTextBoxValue('latitude');
    var longitude = GetTextBoxValue('longitude');
    var marking = GetTextBoxValue('marking');
    var remark = GetTextBoxValue('remark');

    return {
        icao: icao,
        affected: affected,
        obs_type: obs_type,
        elevation: elevation,
        latitude: latitude,
        longitude: longitude,
        marking: marking,
        remark: remark,
        format: format
    };
}
function SetErrorValue(str) {
    $('#error_class').text(str);
}
$('#Preview2D').click(function () {
    $.getJSON('/search', GetTextBoxValues('kml'), function (data) {
        $('#indextable').hide();
        var code = data.code;
        if (code) {
            var url = '/map.html?icao=' + code + '&name=' + '&show3d=false';
            window.open(url, '_blank');
            SetErrorValue('');
        }
        else {
            SetErrorValue(error_value);
        }
    });
});

$('#Download3D').click(function () {
    $.getJSON('/search', GetTextBoxValues('kmz'), function (data) {
        $('#indextable').hide();
        var code = data.code;
        if (code) {
            var url = '/kmz/' + code;
            window.open(url, '_blank');
            SetErrorValue('');
        }
        else {
            SetErrorValue(error_value);
        }
    });
});
var arr = [' ICAO ', ' Affected Area ', ' Obstacle Type ', ' Latitude ', ' Longitude ', ' Elevation ', ' Marking ', ' Remark '];
$('#List').click(function () {
    $.getJSON('/search', GetTextBoxValues('list'), function (array) {
        if (typeof array != "undefined" && array != null && array.length != null && array.length > 0) {
            $('#indextable').show();
            $('#indextable').html("");
            var tab = document.createElement('table');
            tab.classList.add("table","table-hover"); //Pending Testing
            var newthead = document.createElement('thead');
            tab.appendChild(newthead);
            var newtr = document.createElement('tr');
            newthead.appendChild(newtr);
            for (var i = 0; i < arr.length; ++i) {
                var newth = document.createElement('th');
                newth.innerText = arr[i];
                newtr.appendChild(newth);
            }
            var newtbody = document.createElement('tbody');
            tab.appendChild(newtbody);
            // newtbody.appendChild(newtr);
            for (var i = 0; i < array.length; ++i) {
                var newTR = document.createElement('tr');
                var icao = document.createElement('td');
                icao.appendChild(document.createTextNode(array[i].icao));
                newTR.appendChild(icao);
                var affected = document.createElement('td');
                affected.appendChild(document.createTextNode(array[i].affected));
                newTR.appendChild(affected);
                var obs_type = document.createElement('td');
                obs_type.appendChild(document.createTextNode(array[i].obs_type));
                newTR.appendChild(obs_type);
                var latitude = document.createElement('td');
                latitude.appendChild(document.createTextNode(array[i].latitude));
                newTR.appendChild(latitude);
                var longitude = document.createElement('td');
                longitude.appendChild(document.createTextNode(array[i].longitude));
                newTR.appendChild(longitude);
                var elevation = document.createElement('td');
                elevation.appendChild(document.createTextNode(array[i].elevation));
                newTR.appendChild(elevation);
                var marking = document.createElement('td');
                marking.appendChild(document.createTextNode(array[i].marking));
                newTR.appendChild(marking);
                var remark = document.createElement('td');
                remark.appendChild(document.createTextNode(array[i].remark));
                newTR.appendChild(remark);
                newtbody.appendChild(newTR);
            }
            $('#indextable').append(tab);
            SetErrorValue('');
        }
        else {
            $('#indextable').hide();
            SetErrorValue(error_value);
        }
    });
});
