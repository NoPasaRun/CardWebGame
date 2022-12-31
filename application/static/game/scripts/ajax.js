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
                try {
                    let d = JSON.parse(data.response)
                    console.log(d["message"])
                    document.querySelector(".table-wrapper").innerHTML = d["user_data"]
                } catch {
                    console.log("Error occurred. Don't worry, it's accepted.")
                }
            }
        });
    }

    let start_button = document.querySelector("#start-button")
    if (start_button !== null) {
        start_button.addEventListener("click", function() {
            iter_is_allowed = false
        })
    }


    function ajax_loop() {
        if (iter_is_allowed === true) {
            iter_is_allowed = false
            ajax_request("/game/"+lobby_id+"/")
        }
    }

    setInterval(ajax_loop, 500)
})