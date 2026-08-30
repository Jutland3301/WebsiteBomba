const audio = document.getElementById("bgm");
const button = document.getElementById("audio-button");
const icon = document.getElementById("audio-icon");

const audioEntranceScreen =
    document.getElementById("entrance-screen");

if (audio && button) {

    audio.volume = 0.35;

    let enabled =
        localStorage.getItem("bgmEnabled") !== "false";

    function entranceIsActive() {

    const alreadyEntered =
        sessionStorage.getItem("websiteEntered") === "true";

    if (alreadyEntered) {
        return false;
    }

    return Boolean(
        audioEntranceScreen &&
        !audioEntranceScreen.classList.contains(
            "entrance-hidden"
        )
    );
}

    function updateButton() {
        button.classList.toggle("muted", !enabled);

        if (icon) {
            icon.alt = enabled ? "BGM ON" : "BGM OFF";
        }
    }

    async function startAudio() {
        if (!enabled || entranceIsActive()) {
            return;
        }

        try {
            await audio.play();
        } catch {
            // Browser blocked autoplay.
        }
    }

    button.addEventListener("click", async () => {

        enabled = !enabled;

        localStorage.setItem(
            "bgmEnabled",
            String(enabled)
        );

        if (enabled) {
            await startAudio();
        } else {
            audio.pause();
        }

        updateButton();
    });

    if (entranceIsActive()) {

        audio.pause();
        audio.currentTime = 0;

    } else {

        startAudio();
    }

    updateButton();

    if (!audioEntranceScreen) {

        document.addEventListener(
            "click",
            () => {
                if (enabled && audio.paused) {
                    startAudio();
                }
            },
            { once: true }
        );
    }
}