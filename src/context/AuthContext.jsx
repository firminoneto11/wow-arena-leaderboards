import { createContext } from "react";
import { useEffect, useState } from "react";


export const AuthContext = createContext({
    access_token: "",
    expires_in: 1,
    sub: "",
    token_type: ""
});


export function AuthProvider({ children }) {

    const [tokenStuff, setTokenStuff] = useState(null);

    // Função que gera um novo access token
    const getAcessToken = async () => {
        let response;

        try {
            const blizzardTokensUrl = "https://us.battle.net/oauth/token";
            const credentials = process.env.REACT_APP_ENCODED_CREDENTIALS;
            const options = {
                method: "POST",
                headers: {
                    Authorization: credentials,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: "grant_type=client_credentials",
            };
            response = await fetch(blizzardTokensUrl, options);
        }
        catch (error) {
            console.log(error);
            return;
        }

        const data = await response.json();

        if (response.status === 200) {
            setTokenStuff(data);
        }
        else {
            console.log(data);
        }
    }

    useEffect(() => {
        // Gerando um novo access token caso ele não exista!
        getAcessToken();
    }, []);

    const contextData = {
        access_token: tokenStuff ? tokenStuff.access_token : "",
        expires_in: tokenStuff ? tokenStuff.expires_in : 1,
        sub: tokenStuff ? tokenStuff.sub : "",
        token_type: tokenStuff ? tokenStuff.token_type : "",
    }

    return (
        <AuthContext.Provider value={contextData}>
            {children}
        </AuthContext.Provider>
    );
}
