import { Fragment } from "react";
import HelloWorld from "../components/HelloWorld";
import BasePage from "./BasePage";


export default function ThreesLadder() {

    return (
        <Fragment>
            <BasePage />
            <HelloWorld />
            <h1>Página de x3</h1>
        </Fragment>
    );
}
