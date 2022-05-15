import { Fragment } from "react";


export default function Base({ children }) {

    return (
        <Fragment>
            <h1>Base Page</h1>
            {children}
        </Fragment>
    );
}
