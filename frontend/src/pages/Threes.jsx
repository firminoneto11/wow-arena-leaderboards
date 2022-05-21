import Base from "./Base";
import { DataContext } from "../context/DataContext";
import { useContext, useEffect, useState } from "react";


export default function Threes() {

    const { getData } = useContext(DataContext);
    const [data, setData] = useState([]);

    const getApiData = async () => {
        const data = await getData('3s');
        console.log(data);
    }

    useEffect(() => {
        getApiData();
    }, []);

    return (
        <Base>
            <h2>Página de 3s</h2>
        </Base>
    );
}
