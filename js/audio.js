const audio = document.getElementById("bgm");
const button = document.getElementById("audio-button");
const icon = document.getElementById("audio-icon");

if (audio && button) {

    audio.volume = 0.35;

    let enabled =
        localStorage.getItem("bgmEnabled") !== "false";

    function updateButton() {
        button.classList.toggle("muted", !enabled);

        if (icon) {
            icon.alt = enabled ? "BGM ON" : "BGM OFF";
        }
    }

    async function startAudio() {
        if (!enabled) return;

        try {
            await audio.play();
        } catch {
            // Browser blocked autoplay.
            // First user interaction will retry.
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

    // Try autoplay immediately.
    startAudio();
    updateButton();

    // If autoplay was blocked, retry after first interaction.
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