document.addEventListener('DOMContentLoaded', function () {
    'use strict';
    const search_form = document.getElementById("stock_search_form");
    search_form.addEventListener('submit', event => {
        if (!search_form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
        }
        search_form.classList.add('was-validated')
    }, false)
});