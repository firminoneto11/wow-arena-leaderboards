import { BrowserRouter, Routes, Route } from "react-router-dom";
import { DataContextProvider } from "./context/DataContext";
import { MantineProvider } from '@mantine/core';
import { useState } from "react";
import Threes from "./pages/Threes";
import Twos from "./pages/Twos";
import Rbg from "./pages/Rbg";
import "./css/index.css";


export default function App() {

    const themeSettings = {
        colorScheme: 'dark',
        // fontFamily: 'Open Sans Light',
        headings: { fontFamily: 'Open Sans Light' }
    }

    const [theme, setTheme] = useState(themeSettings);

    return (
        <MantineProvider theme={theme}>
            <DataContextProvider>
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Threes />} />
                        <Route path="/2s" element={<Twos />} />
                        <Route path="/rbg" element={<Rbg />} />
                        <Route path="*" />
                    </Routes>
                </BrowserRouter>
            </DataContextProvider>
        </MantineProvider>
    );
}
