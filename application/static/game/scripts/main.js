const size = [window.width, window.height];

$(window).resize(function(){
    window.resizeTo(size[0],size[1]);
});

var last_y = 0;
// DESKTOP

// TRIGGER

// PREVENT DEFAULT HANDLER
function preventDefault(e) {
  e = e || window.event;
  if (e.preventDefault) {
    e.preventDefault();
  }
  e.returnValue = false;
}
// PREVENT SCROLL KEYS
// spacebar: 32, pageup: 33, pagedown: 34, end: 35, home: 36
// left: 37, up: 38, right: 39, down: 40,
// (Source: http://stackoverflow.com/a/4770179)
function keydown(e) {
  var keys = [32,33,34,35,36,37,38,39,40];
  for (var i = keys.length; i--;) {
    if (e.keyCode === keys[i]) {
      preventDefault(e);
      return;
    }
  }
}
// PREVENT MOUSE WHEEL
function wheel(event) {
  event.preventDefault();
  event.stopPropagation();
  return false;
}
// DISABLE SCROLL
function disable_scroll() {
  if (document.addEventListener) {
    document.addEventListener('wheel', wheel, false);
    document.addEventListener('mousewheel', wheel, false);
    document.addEventListener('DOMMouseScroll', wheel, false);
  }
  else {
    document.attachEvent('onmousewheel', wheel);
  }
  document.onmousewheel = document.onmousewheel = wheel;
  document.onkeydown = keydown;

  let x = window.pageXOffset || document.documentElement.scrollLeft
  let y = window.pageYOffset || document.documentElement.scrollTop
  window.onscroll = function() {
    window.scrollTo(x, y);
  };
  // document.body.style.overflow = 'hidden'; // CSS
  disable_scroll_mobile();
}

disable_scroll()

// MOBILE
function disable_scroll_mobile(){
  document.addEventListener('touchmove', preventDefault, false);
}
window.addEventListener('touchmove', function(e){
    let scroll = window.pageYOffset || window.scrollTop || 0;
    let direction = e.changedTouches[0].pageY > last_y ? 1 : -1;
    if(direction > 0 && scroll === 0){
        e.preventDefault();
    }
    last_y = e.changedTouches[0].pageY;
});

window.addEventListener("load", function(){

    //  Function adds special classes for card's cells 
    // in order they are free or locked

    function placeholder_constructor(callback=null) {
        let placeholders = document.querySelectorAll(".placeholder-card-field")
        placeholders.forEach(function(el){
            let cards = $(el).children(".card")
            if (cards.length === 0) {
                el.classList.add("placeholder-card-field-free")
            } else {
                el.classList.add("placeholder-card-field-locked")
            }
        })
        if (callback !== null) {
            callback()
        }
    }

    function distribution(callback=null) {
        let cards = document.querySelectorAll(".buffer-table > .card, .deck > .card")
        cards.forEach(function(el, index) {
            if (index + 1 === cards.length) {
                setTimeout(deck_cards_constructor, 500*index, el, callback)
            } else {
                setTimeout(deck_cards_constructor, 500*index, el)
            }
        })
    }

    function deck_cards_constructor(card, callback=null) {
        let player_id = $(card).attr("data-player")
        let player_deck = document.querySelector("#"+player_id)
        if (player_deck !== null) {
            let length = player_deck.children.length
            let blank_card = card.cloneNode()
            blank_card.style.opacity = "0"
            player_deck.appendChild(blank_card)
            let rect = blank_card.getBoundingClientRect()
            card.style.zIndex = length + ""
            $(card).animate({
                left: rect.left+length*20+"px",
                top: rect.top+"px"
            }, 500, function() {
                    player_deck.removeChild(blank_card)
                    player_deck.appendChild(card)
                    card.style.left = length*20+"px"
                    card.style.top = "0px"
                }
            );
        }
        if (callback !== null) {
            callback()
        }
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

    function player_constructor(callback=null) {
        let width = document.querySelector('.player-nav-list').clientWidth/2
        let height = document.querySelector('.player-nav-list').clientHeight/2
        let angle = 360/document.querySelectorAll(".player-item").length
        
        let sin_beta = Math.sin(-360 * (Math.PI / 180))
        let cos_beta = Math.cos(-360 * (Math.PI / 180))

        let i = 0
        $(".player-item").each(function() {
            let player_cards = $(this).children(".player-description").children(".player-cards")
            let cards = player_cards.children(".card")
            card_constructor(cards)
            i += angle
            let sin_alpha = Math.sin(i * (Math.PI / 180))
            let cos_alpha = Math.cos(i * (Math.PI / 180))

            let Y = Math.floor(height + height * cos_alpha * cos_beta - width * sin_alpha * sin_beta)
            let X = Math.floor(width + height * cos_alpha * sin_beta + width * sin_alpha * cos_beta)
            X -= this.clientWidth/2
            Y -= this.clientHeight/2
            if (X < 0) {
                X = 0
            }
            if (Y < 0) {
                Y = 0
            }
            if (X+this.clientWidth > width*2) {
                X -= X+this.clientWidth-width*2
            }

            if (Y+this.clientHeight > height*2) {
                Y -= Y+this.clientHeight-height*2
            }

            $(this).css("top", Y + "px")
            $(this).css("left", X + "px")
        })
        if (callback !== null) {
            callback()
        }
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
                try {
                    JSON.parse(data)
                } catch {
                    $(".game").html(data)
                    init_game()
                }
            },
            error: function(data) {
                let d = JSON.parse(data.response)
                if (d["url"] !== undefined) {
                    alert("You're out of this game. That means you probably win if someone is still playing.")
                    window.location = d["url"]
                }
            }
        });
    }

    // Function sends a NodeList of card's cells
    // which can be used by user

    function get_zones() {
        let player_cards = document.querySelector(".my-cards")
        let card = player_cards.querySelector(".card")
        let status = card.classList.contains("attacker-card")
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
        const player_cards = document.querySelector(".my-cards")
        const cards = player_cards.querySelectorAll(".card")

        // Function which adds a class to hide card
        // while it is moving

        const dragStart = function (card) {
            setTimeout(() => {
                $(card).attr("is_dragging", true)
                card.classList.add('using-card')
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

        function add_card_and_update(zone, card) {
            zone.append(card)

            card.style.top = "0"
            card.style.left = "0"
            card.style.transform = "rotateZ(0deg)"

            zone.classList.remove("hover-placeholder")

            let csrf_token = document.querySelector("#csrf_token").value;

            let data = {
                "csrf_token": csrf_token,
                "card_value": $(card).attr("data-value"),
                "table_id": $(zone).attr("id")
            }
            let url = window.location.href + 'make_move'
            ajax_request(url, data)
        }

        // If card is user's card and there are no more
        // then 1 card in a cell this Function sends
        // request to backend to save the card in the cell

        const dragDrop = function () {
            let card = document.querySelector(".using-card")
            let card_value = $(card).attr("data-value")
            if (this.children.length < 2 && card_value) {
                add_card_and_update(this, card)
            }
        }

        function find_cross_coords (card_coord, card_size, placeholder_coord, placeholder_size) {
            let cross_coord = 0
            if (card_coord[1] > placeholder_coord[1]) {
                cross_coord = placeholder_size + card_size - card_coord[1] + placeholder_coord[0]
            } else {
                cross_coord = placeholder_size + card_size - placeholder_coord[1] + card_coord[0]
            }
            if (cross_coord < 0) {
                return 0
            } else {
                return cross_coord
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
            card.addEventListener("dragstart", () => dragStart(card))
            card.addEventListener("dragend", () => dragEnd(card))
            card.addEventListener('touchmove', function(e) {
                $(card).attr("is_dragging", true)
                let touchLocation = e.targetTouches[0];
                document.body.appendChild(card)
                card.style.left = touchLocation.pageX + 'px';
                card.style.top = touchLocation.pageY + 'px';
            })
            card.addEventListener("touchend", function(e) {
                $(card).attr("is_dragging", false)
                let card_rect = card.getBoundingClientRect()
                let [x, y] = [
                    [card_rect.left, card_rect.left + card_rect.width],
                    [card_rect.top, card_rect.top + card_rect.height]
                ]
                console.log(x, y)
                let zone_data = {"area": 0, "zone": null}
                zones.forEach(function(el) {
                    let rect = el.getBoundingClientRect()
                    let [z_x, z_y] = [
                        [rect.left, rect.left + rect.width],
                        [rect.top, rect.top + rect.height]
                    ]
                    let x_cross = find_cross_coords(x, card_rect.width, z_x, rect.width)
                    let y_cross = find_cross_coords(y, card_rect.height, z_y, rect.height)
                    if (x_cross*y_cross > zone_data["area"]) {
                        zone_data["zone"] = el
                        zone_data["area"] = x_cross*y_cross
                    }
                })
                let zone = zone_data["zone"]
                let card_value = $(card).attr("data-value")
                if (zone !== null && this.children.length < 2 && card_value) {
                    add_card_and_update(zone, card)
                } else {
                    let player_id = $(card).attr("data-player")
                    let player_deck = document.querySelector("#"+player_id)
                    let length = player_deck.children.length
                    player_deck.appendChild(card)
                    card.style.top = "0px"
                    card.style.left = 20*length + "px"
                }
            })
        })

    }

    function init_game() {
        player_constructor(function callback() {
            distribution(function callback() {
                placeholder_constructor(function callback() {
                    dragAndDrop()
                    create_change_status_button()
                    setInterval(ajax_loop, 500)
                })
            })
        })
    }

    // Infinite functions which call an ajax_request function
    // to update page

    function ajax_loop() {
        let csrf_token = document.querySelector("#csrf_token").value;
        let loop_is_allowed = true
        $(".card").each(function() {
            if ($(this).attr("is_dragging") === 'true') {
                loop_is_allowed = false
            }
        })
        if (loop_is_allowed === true) {
            let data = {"csrf_token": csrf_token}
            ajax_request(window.location, data)
        }
    }

    function create_change_status_button() {
        const c_s_button = document.querySelector("#change_status_button")
        c_s_button.addEventListener("click", function() {
            console.log("smth")
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
        // distribution()
    };
    init_game()
})

