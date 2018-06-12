
function checkSex() {
    //alert('part_sex:' + $('#part_sex').val());
    if ($('#part_sex').val() == '0') {
        if ($('#part_sex').visible() == false) {
            location.href = "#part_sex";
        }
        $('#sexMsg').show();
        return false;
    }
    return true;
}

function checkAge() {
    //alert('part_age:' + $('#part_age').val());
    if ($('#part_age').val() == "" || parseInt($('#part_age').val()) < 18 || parseInt($('#part_age').val()) > 99) {
        if ($('#part_age').visible() == false) {
            location.href = "#part_age";
        }
        $('#ageMsg').show();
        return false;
    }
    return true;
}

function checkLang() {
    //alert('part_lang:' + $('#part_lang').val());
    if ($('#part_lang').val() == '0') {
        if ($('#part_lang').visible() == false) {
            location.href = "#part_lang";
        }
        $('#langMsg').show();
        return false;
    }
    return true;
}



$(document).ready(function() {
     $('#part_sex').change(function() {
        $('#sexMsg').hide();
     });
     $('#part_age').keydown(function() {
        $('#ageMsg').hide();
     });
     $('#part_lang').change(function() {
        $('#langMsg').hide();
     });
	 $('form').on('submit', function() {
	        return checkSex() && checkAge() && checkLang();
     });
});
