
var checkboxes;
var isFirstChooser = true

function showChoice(parent, disabledId) {

    if (disabledId != "" && disabledId != "None") {
        isFirstChooser = false;
    }

	if (disabledId != "") {
		$("#" + disabledId).prop('checked', true);
		$("#" + disabledId).prop('disabled', true);

		$("img[checkId='" + disabledId + "']").css("opacity", "0.5");
	}
	
	checkboxes = $("#" + parent + " table tr td input[type='checkbox']");

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

}
    
    
var smily_checkboxes;
var smily_checkedValue;

function showSmily(parent, checkedValue) {

    smily_checkboxes = $("#" + parent + " table tr td input[type='checkbox']");

    if (typeof(checkedValue) != 'undefined' && checkedValue != "" && checkedValue != "None") {
        for (var i=0; i<smily_checkboxes.length; i++) {
            if($(smily_checkboxes[i]).attr('value') == checkedValue) {
                $(smily_checkboxes[i]).click();
            }
            $(smily_checkboxes[i]).click(function (event) {
                event.preventDefault();
                event.stopPropagation();
                return false;
            });
        }
        smily_checkedValue = checkedValue;
    } else {
        smily_checkboxes.click(function() {
            if (this.checked == true) {
                $('#smilyMsg').hide();
                for (var i=0; i<smily_checkboxes.length; i++) {
                        var id = this.id;
                        try {
                            if ($(smily_checkboxes[i]).prop('disabled') != true) {
                                 if($(smily_checkboxes[i]).attr('id') != id) {
                                     $(smily_checkboxes[i]).prop('checked', false);
                                 }
                             }
                        } catch (e) {
                            //alert (e);
                        }
                    }
                }
            });
    }
}

var leftboxes;

function showChoiceLeft(parent, firstChoice, secondChoice) {

    leftboxes = $("#" + parent + " table tr td input[type='checkbox']");

    for (var i=0; i<leftboxes.length; i++) {
        try {
            if($(leftboxes[i]).attr('id') == firstChoice) {
                $(leftboxes[i]).click();
                $("img[checkId='img" + i + "']").css("opacity", "0.5");
                $(leftboxes[i]).prop('disabled', true);
            }
            if($(leftboxes[i]).attr('id') == secondChoice) {
                $(leftboxes[i]).click();
                $(leftboxes[i]).click(function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    return false;
                });
            } else {
                $(leftboxes[i]).prop('disabled', true);
            }
        } catch (e) {
            //alert (e);
        }
    }
}

function checkChoice() {

    if (typeof(checkboxes) == 'undefined') {
        return true;
    }

    var boxIsChecked = false;

    for (var i=0; i<checkboxes.length; i++) {
        if ($(checkboxes[i]).prop('disabled') != true) {
            if($(checkboxes[i]).prop('checked') == true) {
                boxIsChecked = true;
                if (isFirstChooser) {
                    $('input[name=firstChoice]').val($(checkboxes[i]).attr('id'))
                } else {
                    $('input[name=secondChoice]').val($(checkboxes[i]).attr('id'))
                }
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

function checkSmilies() {

    if (typeof(smily_checkboxes) == 'undefined') {
        return true;
    }

    if(typeof(smily_checkedValue) != 'undefined' ) {
        return true;
    }

    var boxIsChecked = false;

    for (var i=0; i<smily_checkboxes.length; i++) {
        if ($(smily_checkboxes[i]).prop('disabled') != true) {
            if($(smily_checkboxes[i]).prop('checked') == true) {
                boxIsChecked = true;
            }
        }
    }

    if (boxIsChecked) {
        return true;
    } else {
        if ($('#smilies').visible() == false) {
            location.href = "#smilies";
        }
        $('#smilyMsg').show(true);
        return false;
    }
}

function checkSliderFF() {

    // freundlich-feinselig
    var ff_slider = $("input[name$='fb_ff']");
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

function checkSliderFF_half() {

    // freundlich-feinselig half time
    var ff_slider = $("input[name$='_fb_ff_ht']");
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

    // fortsetzen-beenden
    var ff_slider = $("input[name$='fb_fb']");
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
	        var retval = checkChoice() && checkSliderFF() && checkSmilies() && checkSliderFB() && checkSliderFF_half();
            return retval;
     });
});
