
export default function getBlizzEndpoint(session, bracket, accessToken) {
    // session - number
    // bracket - string (3v3, 2v2)
    // accessToken - string
    return `https://us.api.blizzard.com/data/wow/pvp-season/${session}/pvp-leaderboard/${bracket}?namespace=dynamic-us&locale=en_US&access_token=${accessToken}`;
}
