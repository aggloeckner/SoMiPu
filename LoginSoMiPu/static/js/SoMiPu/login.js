

function buildDecisionLabID() {

    var family_name = $("#family_name").val();
    var first_name = $("#first_name").val();
    var birth_month = $("#birth_month").val();
    var birthplace = $("#birthplace").val();
    var asterisk = $("#asterisk").val();
    var birth_number = $("#birth_number").val();

    var decision_lab_id = family_name.trim() + first_name.trim() + birth_month.trim()
                + birthplace.trim() + asterisk.trim() + birth_number.trim();

    $("input[name='decision_lab_id']").val(decision_lab_id);

}

$(document).ready(function() {
	 $('form').on('submit', function() {
            buildDecisionLabID();
            return true;
     });
});
