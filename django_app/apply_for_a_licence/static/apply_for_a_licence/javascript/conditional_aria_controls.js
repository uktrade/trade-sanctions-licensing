document.addEventListener("DOMContentLoaded", function (event) {
    const yesChoice = document.querySelector('input[value="yes"]');
    const noChoice = document.querySelector('input[value="no"]');

    noChoice.addEventListener("change", function () {
        if (this.checked) {
            this.removeAttribute("aria-controls");
        }
    });
    yesChoice.addEventListener("change", function () {
        if (this.checked) {
            yesChoice.setAttribute("aria-controls", conditionalChoiceId);
        }
    });
});
