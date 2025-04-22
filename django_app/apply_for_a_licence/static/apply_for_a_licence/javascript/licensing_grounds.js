document.addEventListener("DOMContentLoaded", function (event) {
    $(document).on('change', 'input[value="unknown"], input[value="none"]', function(){
        if ($(this).is(':checked')) {
            // clear the other inputs
            $('input[name$="licensing_grounds"]').not($(this)).prop('checked', false);
        }
    })

    $('.govuk-checkboxes__divider').prevAll().find('input[name$="licensing_grounds"]').on('change', function () {
        if ($(this).is(':checked')) {
            // clear the unknown grounds input or the none of these input
            $('input[name$="licensing_grounds"][value="unknown"]').prop('checked', false);
            $('input[name$="licensing_grounds"][value="none"]').prop('checked', false);
        }
    });

});
