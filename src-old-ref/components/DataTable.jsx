import { Fragment } from "react";


export default function DataTable({ data }) {

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
