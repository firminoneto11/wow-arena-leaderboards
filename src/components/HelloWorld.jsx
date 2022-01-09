import { Fragment, useContext } from "react";
import { AuthContext } from "../context/AuthContext";


export default function HelloWorld() {

    const context = useContext(AuthContext);

    return (
        <Fragment>
            <h1>{context.access_token}</h1>
            <h1>{context.expires_in}</h1>
            <h1>{context.token_type}</h1>
        </Fragment>
    );
}
