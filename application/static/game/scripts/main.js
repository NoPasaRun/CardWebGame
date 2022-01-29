window.addEventListener("load", function(){

    function card_constructor(all_cards) {
        var angle = -25
        var index = 1
        var left = 0
        var top = 0
        $(all_cards).each(function() {
            var card = this
            let card_info = $(card).children(".card-layout").attr("alt")
            let card_info_fields = $(card).children(".card-info")
            $(card_info_fields).each(function() {
                $(this).text(String(card_info))
            })
            if ([-25, 25].includes(angle)) {
                top = 15
            } else if ([-15, 15].includes(angle)) {
                top = 5
            } else {
                top = 0
            }
            $(card).css("transform", "rotateZ(" + angle + "deg)")
            $(card).css("z-index", index)
            $(card).css("left", left + "px")
            $(card).css("top", top + "px")
            angle += 10
            index++
            left += $(".player-cards").width()/6
        })

    }

    function player_constructor() {
        var width = document.querySelector('.player-nav-list').clientWidth/2
        var height = document.querySelector('.player-nav-list').clientHeight/2
        var angle = 360/document.querySelectorAll(".player-item").length
        
        var sin_beta = Math.sin(-360 * (Math.PI / 180))
        var cos_beta = Math.cos(-360 * (Math.PI / 180))

        var i = 0
        $(".player-item").each(function() {
            let cards = $(this).children(".player-description").children(".player-cards").children(".card")
            card_constructor(cards)
            i += angle
            var sin_alpha = Math.sin(i * (Math.PI / 180))
            var cos_alpha = Math.cos(i * (Math.PI / 180))

            var X = Math.floor(height + height * cos_alpha * cos_beta - width * sin_alpha * sin_beta)  
            var Y = Math.floor(width + height * cos_alpha * sin_beta + width * sin_alpha * cos_beta)  
            
            y_add_offset = this.clientWidth/2
            x_add_offset = this.clientHeight/1.5

            $(this).css("top", X-x_add_offset + "px")
            $(this).css("left", Y-y_add_offset + "px")
        })
    }

    const dragAndDrop = () => {
        const zones = document.querySelectorAll(".placeholder-card-field")
        const cards = document.querySelectorAll(".my-card")

        const dragStart = function () {
            setTimeout(() => {
                this.classList.add('using-card')
            }, 0)
        }

        const dragEnd = function (card, left, top, transform) {
            card.classList.remove('using-card')
        }

        const dragOver = function (event) {
            event.preventDefault()
        }

        const dragEnter = function () {
            this.classList.add("hover-placeholder")
        }

        const dragLeave = function () {
            this.classList.remove("hover-placeholder")
        }

        const dragDrop = function () {
            my_card = $(this).children(".my-card")
            if (my_card.length == 0) {
                let card = document.querySelector(".using-card")
                this.append(card)
                card.style.top = 0
                card.style.left = 0
                card.style.transform = "rotateZ(45deg)"
                card.classList.remove(".my-card")
                this.classList.remove("hover-placeholder")
            }
        }

        zones.forEach((el) => {
            el.addEventListener("dragover", dragOver)
            el.addEventListener("dragenter", dragEnter)
            el.addEventListener("dragleave", dragLeave)
            el.addEventListener("drop", dragDrop)
        })

        cards.forEach(function(card){
            var info = $(card).css("left")
            card.addEventListener("dragstart", dragStart)
            card.addEventListener("dragend", () => dragEnd(card))
        })
    }

    function ajax_loop() {
        let csrf_token = document.querySelector("#csrf_token").value;
        $.ajax({
            url: '/game/1/',
            type: 'post',
            dataType: 'html',
            cache: false,
            async: false,
            data: {"csrf_token": csrf_token, "update-page": true},
            success: function(data) {
                $("body").html(data)
                dragAndDrop()
                player_constructor()
            }
        });
    }

    window.onresize = function() {
        player_constructor()
    };
    dragAndDrop()
    player_constructor()
    setInterval(ajax_loop, 5000)
})

