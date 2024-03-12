function updateDynamicText(element) {
    var dynamicTextElement = document.getElementById(element);
    var text = "";

    for (var i = 0; i < 4; i++) {
        setTimeout(function() {
            dynamicTextElement.textContent = text;
            text += " .";
        }, i * 1000);
    }
}

function runBasedOnTemplate() {
    var mobileTemplate = document.getElementById("mobile-template");
    var desktopTemplate = document.getElementById("desktop-template");
    var mobileDisplayStyle = window.getComputedStyle(mobileTemplate).getPropertyValue("display");
    var desktopDisplayStyle = window.getComputedStyle(desktopTemplate).getPropertyValue("display");

    if (mobileDisplayStyle !== 'none') {
        updateDynamicText('dynamic-text');
    } else if (desktopDisplayStyle !== 'none') {
        updateDynamicText('dynamic-text2');
    }
}

runBasedOnTemplate();
setInterval(runBasedOnTemplate, 4000);

function showWho() {
    showWhoButton = document.getElementById('show-who-button');
    showWhoButton.style.display = 'none';
    spinner = document.getElementById('spinner1');
    spinner.style.display = 'block';
    setTimeout(function() {
        showWhoButton = document.getElementById('show-who-button');
        spinner = document.getElementById('spinner1');
        registeredSection = document.getElementById('registered-section');
        spinner.style.display = 'none';
        registeredSection.style.display = 'block';
        window.scrollBy(0, 500);
    }, 1000);


}

document.addEventListener("DOMContentLoaded", function() {
    // Check if there are errors in the form
    function scrollToError() {
        var mobileTemplate = document.getElementById("mobile-template");
        var desktopTemplate = document.getElementById("desktop-template");
        var mobileDisplayStyle = window.getComputedStyle(mobileTemplate).getPropertyValue("display");
        var desktopDisplayStyle = window.getComputedStyle(desktopTemplate).getPropertyValue("display");
        var formErrors = document.querySelectorAll(".error-source");
    
        if (mobileDisplayStyle !== 'none') {
            formError = formErrors[0];
        } else if (desktopDisplayStyle !== 'none') {
            formError = formErrors[1];
        }
    
        formError.closest('.mb-3').scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest'
        });
    }
    scrollToError();
});