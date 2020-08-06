error_value = "Invalid Obstacle";
function SetErrorValue(str) {
    $('#error_class').text(str);
}

function GetTextBoxValue(id) {
    return document.getElementById(id).value;
}
function GetTextBoxValues() {
    var icao = GetTextBoxValue('icao');
    icao = icao.toUpperCase();
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
        remark: remark
    };
}

$('#Submit_Obstacle').click(function () {
    obs=GetTextBoxValues();
    
    if((obs.icao.length != 4) || (obs.affected.length == 0) || (obs.obs_type.length == 0) || (isNaN(obs.elevation)) || (isNaN(obs.latitude)) || (isNaN(obs.longitude)) || (obs.remark.length == 0) || (obs.elevation.length == 0) || (obs.latitude.length != 9) || obs.longitude.length != 9) {
        SetErrorValue(error_value);
        console.log("Invalid Obstacle here");
        console.log(obs);
        return;
    }    
    
    console.log("Valid Obstacle");
    console.log(obs);
    $.getJSON('/add_obs', GetTextBoxValues(), function (data) {
        $('#indextable').hide();
        console.log(data);
        
        if(data.reply) {
            SetErrorValue("Updated Successfully");
        } 
        else {
            SetErrorValue("Obstacle Already Exists / Unable to Add Obstacle");
        }
    });
});

