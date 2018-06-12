
var loginCounter = 0;
var checkResult = "";

function isANumber(str){
  return !/\D/.test(str);
}

function checkCrossSum(inputString) {

    var firstFiveDigits = inputString.substring(0, 5);
    var checksum = inputString.substring(5);

    var fiveDigits = firstFiveDigits.split("");
    var sumOfFirstFiveDigits = 0;

    for (var i=0; i<fiveDigits.length; i++) {
        sumOfFirstFiveDigits += parseInt(fiveDigits[i]);
    }

    var valueOfChecksum = parseInt(checksum);

    if (sumOfFirstFiveDigits == valueOfChecksum) {
        return 0;
    } else {
        return -1;
    }

}


function checkLengthAndContent(inputString) {

    if (typeof (inputString) == 'undefined' || inputString == null) {
        return "Bitte geben Sie Ihre DecisionLab-ID ein.";
    }

    if (inputString.length != 7) {
        return "Die DecisionLab-ID muss siebenstellig eingegeben werden.";
    }

    if (!isANumber(inputString)) {
        return "Die Decision-Lab-ID darf nur Ziffern enthalten.";
    }

    if (checkCrossSum(inputString) != 0) {
        return "Die eingegebene DecisionLab-ID ist ungültig.";
    }

    return "OK";

}


function checkDecisionLabID(input) {

    var msg = checkLengthAndContent(input);

    if (msg == "OK") {
        return true;
    } else {
        checkResult = msg;
        loginCounter = loginCounter + 1;
        if (loginCounter < 3) {
            alert (msg);
        } else {
            var myDiv = $('#goodby');
            $('form').remove();
            if ($('.well').length > 0) {
                $('.well').remove();
            }
            $('.page-header').append(myDiv);
            $('#goodby').show();
        }
        return false;
    }

}

$(document).ready(function() {
	 $('form').on('submit', function() {
	        var input = $('#decision_lab_id').val();
            return checkDecisionLabID(input);
     });
});
