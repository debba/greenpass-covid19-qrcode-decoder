(function(document, i18n) {
    document.addEventListener("DOMContentLoaded", function () {
        var form = document.getElementById('greenform'),
        pickFileInput = document.getElementById('pickFileInput');

        form.addEventListener('submit', function (e) {
            if (pickFileInput.files.length === 0){
                alert(i18n.select_before);
                e.preventDefault();
            }
        });
    });

})(document, i18n);