window.addEventListener("load", function(){

    //  Function adds special classes for card's cells 
    // in order they are free or locked

    function placeholder_constructor() {
        let placeholders = document.querySelectorAll(".placeholder-card-field")
        placeholders.forEach(function(el){
            let cards = $(el).children(".card")
            if (cards.length === 0) {
                el.classList.add("placeholder-card-field-free")
            } else {
                el.classList.add("placeholder-card-field-locked")
            }
        })
    }

    // Function transforms cards in the right position
    // and adds an Z-angle for them

    function card_constructor(all_cards) {
        let index = 0
        let left = 0
        $(all_cards).each(function() {
            this.style.zIndex = index + ""
            this.style.left = left + "px"
            index++
            left += 20
        })
    }

    // Function transforms positions of players in a way
    // the distances would be the same between them

    function player_constructor() {
        let width = document.querySelector('.player-nav-list').clientWidth/2
        let height = document.querySelector('.player-nav-list').clientHeight/2
        let angle = 360/document.querySelectorAll(".player-item").length
        
        let sin_beta = Math.sin(-360 * (Math.PI / 180))
        let cos_beta = Math.cos(-360 * (Math.PI / 180))

        let i = 0
        $(".player-item").each(function() {
            let cards = $(this).children(".player-description").children(".player-cards").children(".card")
            card_constructor(cards)
            i += angle
            let sin_alpha = Math.sin(i * (Math.PI / 180))
            let cos_alpha = Math.cos(i * (Math.PI / 180))

            let X = Math.floor(height + height * cos_alpha * cos_beta - width * sin_alpha * sin_beta)
            let Y = Math.floor(width + height * cos_alpha * sin_beta + width * sin_alpha * cos_beta)
            
            let y_add_offset = this.clientWidth/2
            let x_add_offset = this.clientHeight/1.5

            $(this).css("top", X-x_add_offset + "px")
            $(this).css("left", Y-y_add_offset + "px")
        })
    }

    // The function send ajax request to update page
    // without reloading

    function ajax_request(url, request_data) {
        $.ajax({
            url: url,
            type: 'post',
            dataType: 'html',
            cache: false,
            async: false,
            data: request_data,
            success: function(data) {
                $(".game").html(data)
                init_game()
            }
        });
    }

    // Function sends a NodeList of card's cells
    // which can be used by user

    function get_zones() {
        let card = document.querySelector(".my-card")
        let status = card.classList.contains("attacker_card")
        if (status) {
            return document.querySelectorAll(".placeholder-card-field-free")
        } else {
            return document.querySelectorAll(".placeholder-card-field-locked")
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
                let placeholder = $(this).children(".card")
                if (placeholder.length < 2) {
                    this.append(card)

                    card.style.top = "0"
                    card.style.left = "0"
                    card.style.transform = "rotateZ(0deg)"
    
                    this.classList.remove("hover-placeholder")

                    zones.forEach((el) => {
                        el.removeEventListener("dragover", dragOver)
                        el.removeEventListener("dragenter", dragEnter)
                        el.removeEventListener("dragleave", dragLeave)
                        el.removeEventListener("drop", dragDrop)
                    })
                    let csrf_token = document.querySelector("#csrf_token").value;
                    let card_value = $(card).attr("data-value")

                    let data = {"csrf_token": csrf_token, "card_value": card_value, "table_id": $(this).attr("id")}
                    let url = window.location.href + 'make_move'
                    let func = function(data) {
                        $(".game").html(data)
                        init_game()
                    }
                    ajax_request(url, data, func)
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

    function init_game() {
        placeholder_constructor()
        dragAndDrop()
        player_constructor()
        create_change_status_button()
    }

    // Infinite functions which call an ajax_request function
    // to update page

    function ajax_loop() {
        let csrf_token = document.querySelector("#csrf_token").value;
        let loop_is_allowed = true
        $(".my-card").each(function() {
            if ($(this).attr("is_dragging") === 'true') {
                loop_is_allowed = false
            }
        })
        if (loop_is_allowed === true) {
            let data = {"csrf_token": csrf_token}
            ajax_request(window.location.href, data)
        }
    }

    function create_change_status_button() {
        const c_s_button = document.querySelector("#change_status_button")
        c_s_button.addEventListener("click", function() {
            let url = window.location.href + 'change_status'
            let csrf_token = document.querySelector("#csrf_token").value;
            let data = {"csrf_token": csrf_token}
            ajax_request(url, data)
        })
    }

    // Calling methods if page was updated by
    // user (GET request)

    window.onresize = function() {
        player_constructor()
    };
    init_game()
    setInterval(ajax_loop, 3000)
})

