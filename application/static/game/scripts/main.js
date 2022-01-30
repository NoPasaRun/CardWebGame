window.addEventListener("load", function(){

    //  Function adds special classes for card's cells 
    // in order they are free or locked

    function placeholder_constructor() {
        let placeholders = document.querySelectorAll(".placeholder-card-field")
        placeholders.forEach(function(el){
            if ($(el).children(".card").length == 0) {
                el.classList.add("placeholder-card-field-free")
            } else {
                el.classList.add("placeholder-card-field-locked")
            }
        })
    }

    // Function changes the color of cards to red if they
    // have these images "♦", "♥"

    function change_color() {
        $(".card").each(function(){
            var mast = $(this).children(".card-layout").attr("alt")
            if(mast) {
                if (mast.includes("♦") || mast.includes("♥")) {
                    this.style.color = "red"
                }
            }
        })
    }

    // Function transforms cards in the right position
    // and adds an Z-angle for them

    function card_constructor(all_cards) {
        var angle = -25
        var index = 1
        var left = 0
        var top = 0
        $(all_cards).each(function() {
            var card = this
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

    // Function transforms positions of players in a way
    // the distances would be the same between them

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

    // The function send ajax request to update page
    // without reloading

    function ajax_request(request_data) {
        $.ajax({
            url: '/game/1/',
            type: 'post',
            dataType: 'html',
            cache: false,
            async: false,
            data: request_data,
            success: function(data) {
                $("body").html(data)
                change_color()
                placeholder_constructor()
                dragAndDrop()
                player_constructor()
            }
        });
    }

    // Function sends a NodeList of card's cells
    // which can be used by user

    function get_zones() {
        var card = document.querySelector(".my-card")
        var state = $(card).attr("state")
        if (state == "attack") {
            return document.querySelectorAll(".placeholder-card-field-free")
        } else if (state == "defend") {
            return document.querySelectorAll(".placeholder-card-field-locked")
        } else {
            return document.querySelectorAll(".placeholder-card-field")
        }
    }

    // Function creates functions of dragging and dropping
    // cards into cells

    const dragAndDrop = () => {
        const zones = get_zones()
        const cards = document.querySelectorAll(".my-card")

        // Function which adds a class to hide card
        // while it is moving

        const dragStart = function () {
            setTimeout(() => {
                $(this).attr("is_dragging", true)
                this.classList.add('using-card')
            }, 0)
        }

        // Function which remove a hide class
        // when card returns to its origin place

        const dragEnd = function (card) {
            $(card).attr("is_dragging", false)
            card.classList.remove('using-card')
        }

        // Function prevents smth when card is over
        // the cell

        const dragOver = function (event) {
            event.preventDefault()
        }

        // Function which add a style class
        // for cell when a card is over

        const dragEnter = function () {
            this.classList.add("hover-placeholder")
        }

        // Function which removes a style class
        // from cell when card leaves an area

        const dragLeave = function () {
            this.classList.remove("hover-placeholder")
        }

        // If card is user's card and there are no more
        // then 1 card in a cell this Function sends
        // request to backend to save the card in the cell

        const dragDrop = function () {
            let card = document.querySelector(".using-card")
            if ($(card).hasClass("my-card")) {
                my_card = $(this).children(".card")
                let csrf_token = document.querySelector("#csrf_token").value;
                if (my_card.length < 2) {
                    this.append(card)

                    card.style.top = 0
                    card.style.left = 0
                    card.style.transform = "rotateZ(0deg)"
    
                    this.classList.remove("hover-placeholder")
    
                    card_value = $(card).children(".card-layout").attr("alt")
                    data = {"csrf_token": csrf_token, "update-table": true, "continue-move": true,
                            "update-page": true, "card": card_value, "place_id": $(this).attr("id")}
    
                    ajax_request(data)
                }
            }
        }

        // Adding event listeners

        zones.forEach((el) => {
            el.addEventListener("dragover", dragOver)
            el.addEventListener("dragenter", dragEnter)
            el.addEventListener("dragleave", dragLeave)
            el.addEventListener("drop", dragDrop)
        })

        cards.forEach(function(card){
            card.addEventListener("dragstart", dragStart)
            card.addEventListener("dragend", () => dragEnd(card))
        })
    }

    // Infinite functions which call an ajax_request function
    // to update page

    function ajax_loop() {
        let csrf_token = document.querySelector("#csrf_token").value;
        var loop_is_allowed = true
        $(".my-card").each(function() {
            if ($(this).attr("is_dragging") == 'true') {
                loop_is_allowed = false
            }
        })
        if (loop_is_allowed == true) {
            ajax_request({"csrf_token": csrf_token, "update-page": true})
        }
    }

    // Calling methods if page was updated by
    // user (GET request)

    window.onresize = function() {
        player_constructor()
    };
    change_color() 
    placeholder_constructor()
    dragAndDrop()
    player_constructor()
    const looper = setInterval(ajax_loop, 5000)
})

