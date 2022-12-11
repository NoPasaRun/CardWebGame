window.addEventListener("load", function() {

    var iter_is_allowed = true

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
                iter_is_allowed = true
                console.log("Error occurred. Don't worry, it's accepted.")
            }
        });
    }


    document.querySelector("#start-button").addEventListener("click", function() {
        iter_is_allowed = false
    })


    function ajax_loop() {
        if (iter_is_allowed === true) {
            iter_is_allowed = false
            ajax_request("/game/"+lobby_id+"/")
        }
    }

    setInterval(ajax_loop, 500)
})