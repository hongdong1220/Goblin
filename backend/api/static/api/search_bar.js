document.addEventListener('DOMContentLoaded', function () {
    'use strict';
    const search_form = document.getElementById("stock_search_form");
    const tooltip = document.getElementById("stock_input_tooltips");

    search_form.addEventListener('submit', async (event) => {
        event.preventDefault();
        event.stopPropagation();
        const ticker_input = document.getElementById("ticker_input")
        const ticker = ticker_input.value.trim().toUpperCase();
        if (!search_form.checkValidity()) {
            console.log("Please enter a ticker!");
            tooltip.innerText = "Please enter a ticker!";
        } else {
            // Checks if the input value is a valid ticker. If so search it, 
            // otherwise stay on the same page 
            let api_response = await fetch(`api_is_valid_ticker/${ticker}`).then(response => response.json());
            let isValid = api_response['response'];
            if (!isValid) {
                tooltip.innerText = `${ticker} doesn't exist!`;
                ticker_input.value = "";
            } else {
                search_form.submit();
            }

        }
        search_form.classList.add('was-validated');
    }, false)
});

