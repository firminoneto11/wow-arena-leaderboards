import { Fragment, useContext, useState, useEffect } from "react";
import { AuthContext } from "../context/AuthContext";
import mountData from '../utils/fetchAndMountData';


export default function DataTable() {

    const [data, setData] = useState(null);

    const { access_token } = useContext(AuthContext);

    const setDataHandler = (newData) => {
        setData(newData);
    }

    useEffect(() => {
        if (access_token) {
            mountData(31, "3v3", access_token, setDataHandler);
        }
    }, []);

    return (
        <Fragment>
            <table>
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>CR</th>
                        <th>Reino</th>
                    </tr>
                </thead>
                <tbody>
                    {data && data.map(player => {
                        return (
                            <tr key={player.character.id}>
                                <td>{player.character.name}</td>
                                <td>{player.rating}</td>
                                <td>{player.character.realm.slug}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </Fragment>
    );
}
