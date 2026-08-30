const entranceScreen =
    document.getElementById("entrance-screen");

const entranceButton =
    document.getElementById("entrance-button");

const entranceAudio =
    document.getElementById("bgm");


if (entranceScreen && entranceButton) {

    entranceButton.addEventListener(
        "click",
        async () => {

            const enabled =
                localStorage.getItem("bgmEnabled") !== "false";

            if (enabled && entranceAudio) {

                try {
                    await entranceAudio.play();
                } catch {
                    // Continue entering even if playback fails.
                }
            }

            entranceScreen.classList.add(
                "entrance-hidden"
            );

            setTimeout(
                () => {
                    entranceScreen.remove();
                },
                250
            );
        }
    );
}