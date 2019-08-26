function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
$(function(){
    console.log("main.js imported")
})
function initProvinceChange(){
    let provinces = $("#id_address_province").find("option")
    let districts = $("#id_address_district").find("option")
    // console.log(provinces)
    let selected_province = $("#id_address_province").val()
    let selected_district = $("#id_address_district").val()
    let provinceDistrictJson = {}
    for(let i=0; i<provinces.length; i++){
        // console.log(provinces[i].value)
        provinceDistrictJson[provinces[i].value] = $("#id_address_district").find("option[value^="+provinces[i].value+"]")
    }
    $("#id_address_district").empty()
    for(let i=0; i<provinceDistrictJson[selected_province].length; i++){
        let newOption = new Option(provinceDistrictJson[selected_province][i].text, provinceDistrictJson[selected_province][i].value, false, false);
        $("#id_address_district").append(newOption)
    }
    $("#id_address_district").val(selected_district)
    
    $("#id_address_province").on("change", function(){
        let provinceCode = $(this).val()
        $("#id_address_district").empty()
        for(let i=0; i<provinceDistrictJson[provinceCode].length; i++){
            let newOption = new Option(provinceDistrictJson[provinceCode][i].text, provinceDistrictJson[provinceCode][i].value, false, false);
            $("#id_address_district").append(newOption).trigger("change")
        }
    })
}