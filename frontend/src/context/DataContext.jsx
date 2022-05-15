import { createContext } from "react";
import axios from "axios";


export const DataContext = createContext();


export const DataContextProvider = ({ children }) => {

    const requestsLinks = {
        baseUrl: "http://localhost:8000/",
        endpoint3s: "threes_data/",
        endpoint2s: "twos_data/",
        endpointRbg: "rbg_data/",
    }

    const fetcher = axios.create({
        baseURL: requestsLinks.baseUrl
    });

    const getData = async (tipo) => {
        let endpoint;

        if (tipo === '3s') {
            endpoint = requestsLinks.endpoint3s;
        }
        else if (tipo === '2s') {
            endpoint = requestsLinks.endpoint2s;
        }
        else {
            endpoint = requestsLinks.endpointRbg;
        }

        try {
            const response = await fetcher.get(endpoint);
            return response.data;
        }
        catch (error) {
            console.log(error);
            return null;
        }

    }

    const contextData = {
        getData, fetcher
    }

    return (
        <DataContext.Provider value={contextData}>
            {children}
        </DataContext.Provider>
    );

}
