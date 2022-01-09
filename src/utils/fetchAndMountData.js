

export default async function mountData(session, bracket, accessToken, setDataHandler) {

    const leaderboardsUrl = `https://us.api.blizzard.com/data/wow/pvp-season/${session}/pvp-leaderboard/${bracket}?namespace=dynamic-us&locale=en_US&access_token=${accessToken}`;

    console.log(leaderboardsUrl);

    let response;

    try {
        response = await fetch(leaderboardsUrl);
    }
    catch (error) {
        console.log(error);
        setDataHandler(false);
        return;
    }

    if (response.status === 200) {
        const players = await response.json();

        const brazilianRealms = ["azralon", "nemesis", "goldrinn", "gallywix", "tol-barad"];

        const brazilianPlayers = players && players.entries.filter(player => {
            return brazilianRealms.includes(player.character.realm.slug);
        });

        setDataHandler(brazilianPlayers);

    }
    else {
        setDataHandler(false);
    }

}
