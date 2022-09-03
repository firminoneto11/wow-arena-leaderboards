import { createContext } from "react";
import axios from "axios";


export const DataContext = createContext();


export const DataContextProvider = ({ children }) => {

    const requestsLinks = {
        baseUrl: "http://localhost:8000/",
        endpoint: "data/"
    }

    const fetcher = axios.create({
        baseURL: requestsLinks.baseUrl
    });

    const getData = async (tipo) => {
        const endpoint = requestsLinks.endpoint + tipo + "/";
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
