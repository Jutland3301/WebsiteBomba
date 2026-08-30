const entranceScreen =
    document.getElementById("entrance-screen");

const entranceButton =
    document.getElementById("entrance-button");

const entranceAudio =
    document.getElementById("bgm");


if (entranceScreen && entranceButton) {

    const alreadyEntered =
        sessionStorage.getItem("websiteEntered") === "true";

    if (alreadyEntered) {

        document.documentElement.classList.remove(
            "show-entrance"
        );

        entranceScreen.remove();

    } else {

        entranceButton.addEventListener(
            "click",
            async () => {

                sessionStorage.setItem(
                    "websiteEntered",
                    "true"
                );

                document.documentElement.classList.remove(
                    "show-entrance"
                );

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
}