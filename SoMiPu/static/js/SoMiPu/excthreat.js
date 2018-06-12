
function checkExcThreat() {

    var radios = $("input[type='radio']");

    if (radios.length == 0) {
        return true;
    }

    var isClicked = false;

    for (var i=0; i<radios.length; i++) {
        if ($(radios[i]).is(":checked")) {
            isClicked = true;
        }
    }

    if (isClicked) {
        return true;
    } else {
        $('#termMsg').show();
        $('#rbTerminate').mouseup(function() {
                $('#termMsg').hide();
            });
        $('#rbGoon').mouseup(function() {
                $('#termMsg').hide();
            });
        return false;
    }

}

$(document).ready(function() {
	 $('form').on('submit', function() {
	        var retval = checkExcThreat();
            return retval;
     });
});
