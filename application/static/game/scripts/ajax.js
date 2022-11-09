window.addEventListener("load", function() {

    function ajax_request(url) {
        $.ajax({
            url: url,
            type: 'get',
            dataType: 'html',
            cache: false,
            async: false,
            success: function() {
                window.location = url
            },
            error: function(data) {
                console.log("Error occurred. Don't worry, it's accepted.")
            }
        });
    }


    function ajax_loop() {
        ajax_request("/game/"+lobby_id+"/")
    }

    setInterval(ajax_loop, 500)
})