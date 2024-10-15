document.addEventListener("DOMContentLoaded", function (event) {
    const yesChoice = document.querySelector('input[value="yes"]');
    const noChoice = document.querySelector('input[value="no"]');

    noChoice.removeAttribute("aria-controls");
    yesChoice.setAttribute("aria-controls", conditionalChoiceId);
});
