import { Fragment, useContext, useEffect, useState } from "react";
import DataTable from "../components/DataTable";
import { AuthContext } from "../context/AuthContext";
import BasePage from "./BasePage";
import mountData from '../utils/fetchAndMountData';


export default function ThreesLadder() {

    const [data, setData] = useState(null);
    const { access_token } = useContext(AuthContext);

    const pvpSession = 32;
    const bracket = "3v3";

    useEffect(() => {
        if (access_token) {
            mountData(pvpSession, bracket, access_token, setData);
        }
    }, [access_token]);

    return (
        <Fragment>
            <BasePage />
            <h1>Página de x3</h1>
            <DataTable data={data} />
        </Fragment>
    );
}
