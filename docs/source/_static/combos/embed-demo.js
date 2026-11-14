(function () {
    var marks = document.querySelectorAll(".combos-embed-demo [data-ran]");
    marks.forEach(function (el) {
        el.textContent = "The script ran.";
    });
}());
