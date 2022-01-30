window.addEventListener("load", function() {
    const music = new Audio('/static/index/music/poker.mp3');
    music.loop = true;
    music.play()
    const music_button = document.querySelector("#music-button")
    music_button.addEventListener("click", function(){
        if (music.paused) {
            music_button.style.backgroundImage = "url('/static/index/images/play-button.png')"
            music.play()
        } else {
            music_button.style.backgroundImage = "url('/static/index/images/stop-button.png')"
            music.pause()
        }
    })
})