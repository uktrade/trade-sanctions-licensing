document.addEventListener("DOMContentLoaded", function (event) {
    $(document).on('change', 'input[value="Unknown grounds"], input[value="None of these"]', function(){
        if ($(this).is(':checked')) {
            // clear the other inputs
            $('input[name$="licensing_grounds"]').not($(this)).prop('checked', false);
        }
    })

    $('.govuk-checkboxes__divider').prevAll().find('input[name$="licensing_grounds"]').on('change', function () {
        if ($(this).is(':checked')) {
            // clear the unknown regime input
            $('input[name$="licensing_grounds"][value="Unknown grounds"]').prop('checked', false);
            $('input[name$="licensing_grounds"][value="None of these"]').prop('checked', false);
        }
    });

});
