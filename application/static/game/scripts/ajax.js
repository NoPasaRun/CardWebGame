window.addEventListener("load", function() {
    function ajax_request(url, request_data) {
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'html',
            cache: false,
            async: false,
            data: request_data,
            success: function() {
                window.location = url
            },
            error: function(data) {
                console.log("Error occurred. Don't worry, it's accepted.")
            }
        });
    }


    function ajax_loop() {
        let csrf_token = document.querySelector("#csrf_token").value;
        let data = {"csrf_token": csrf_token}
        ajax_request("/game/1/", data)
    }

    setInterval(ajax_loop, 500)
})