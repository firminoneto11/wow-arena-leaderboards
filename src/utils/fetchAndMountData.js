

export default async function mountData(session, bracket, accessToken, setData) {

    const leaderboardsUrl = `https://us.api.blizzard.com/data/wow/pvp-season/${session}/pvp-leaderboard/${bracket}?namespace=dynamic-us&locale=en_US&access_token=${accessToken}`;

    let response;

    try {
        response = await fetch(leaderboardsUrl);
    }
    catch (error) {
        console.log(error);
        setData(false);
        return;
    }

    if (response.status === 200) {
        const players = await response.json();

        const brazilianRealms = ["azralon", "nemesis", "goldrinn", "gallywix", "tol-barad"];

        const brazilianPlayers = players && players.entries.filter(player => {
            return brazilianRealms.includes(player.character.realm.slug);
        });

        setData(brazilianPlayers);

    }
    else {
        setData(false);
    }

}

// -> Endpoint de avatar
// https://us.api.blizzard.com/profile/wow/character/dalaran/kalvish/character-media?namespace=profile-us&locale=en_US&access_token=${access_token}

// -> Endpoint de perfil
// https://us.api.blizzard.com/profile/wow/character/dalaran/kalvish?namespace=profile-us&locale=en_US&access_token=${access_token}
