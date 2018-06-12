
var checkboxes = $("#choice table tr td input[type='checkbox']");

checkboxes.click(function() {
    if (this.checked == true) {
        $('#choiceMsg').hide();
        for (var i=0; i<checkboxes.length; i++) {
            var id = this.id;
                try {
                    if ($(checkboxes[i]).prop('disabled') != true) {
                        if($(checkboxes[i]).attr('id') != id) {
                            $(checkboxes[i]).prop('checked', false);
                        }
                    }
                } catch (e) {
                    //alert (e);
                }
        }
    }

});


var smilies = $("#smilies table tr td input[type='checkbox']");

smilies.click(function() {
    if (this.checked == true) {

        for (var i=0; i<smilies.length; i++) {
            var id = this.id;
            try {
                if ($(smilies[i]).prop('disabled') != true) {
                    if($(smilies[i]).attr('id') != id) {
                        $(smilies[i]).prop('checked', false);
                    }
                }
            } catch (e) {
                //alert (e);
            }
        }
    }

});


function checkChoice() {

    var boxIsChecked = false;

    for (var i=0; i<checkboxes.length; i++) {
        if ($(checkboxes[i]).prop('disabled') != true) {
            if($(checkboxes[i]).prop('checked') == true) {
                boxIsChecked = true;
            }
        }
    }

    if (boxIsChecked) {
        return true;
    } else {
        if ($('#choice').visible() == false) {
            location.href = "#choice";
        }
        $('#choiceMsg').show(true);
        return false;
    }
}

function checkSliderFF() {

    var ff_slider = $("input[name='Assess']");
    if (ff_slider.length == 1) {
        if ($(ff_slider).val() == '-9') {
            if ($('#vas_ff').visible() == false) {
                location.href = "#vas_ff";
            }
            $('#vas_fb_ff').show();
            $('#cross0div').mouseup(function() {
                $('#vas_fb_ff').hide();
            });
            return false;
        } else {
            return true;
        }
    }

    return true;
}

function checkSliderFB() {

    var ff_slider = $("input[name='Exclusion']");
    if (ff_slider.length == 1) {
        if ($(ff_slider).val() == '-9') {
            if ($('#vas_fb').visible() == false) {
                location.href = "#vas_fb";
            }
            $('#vas_fb_fb').show();
            $('#cross1div').mouseup(function() {
                $('#vas_fb_fb').hide();
            });
            return false;
        } else {
            return true;
        }
    }

    return true;
}

$(document).ready(function() {
	 $('form').on('submit', function() {
            return checkChoice() && checkSliderFF() && checkSliderFB();
     });
});



