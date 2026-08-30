const audio = document.getElementById("bgm");
const button = document.getElementById("audio-button");

if (audio && button) {

    // Default volume
    audio.volume = 0.35;

    // Check whether BGM was playing on previous page
    const shouldPlay = sessionStorage.getItem("bgmPlaying") === "true";

    if (shouldPlay) {
        audio.play()
            .then(() => {
                button.textContent = "STOP";
            })
            .catch(() => {
                // Browser blocked autoplay.
                button.textContent = "PLAY";
                sessionStorage.setItem("bgmPlaying", "false");
            });
    }

    button.addEventListener("click", () => {

        if (audio.paused) {

            audio.play();

            button.textContent = "STOP";
            sessionStorage.setItem("bgmPlaying", "true");

        } else {

            audio.pause();

            button.textContent = "PLAY";
            sessionStorage.setItem("bgmPlaying", "false");
        }
    });
}