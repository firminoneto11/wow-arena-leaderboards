import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { DataContextProvider } from "./context/DataContext";
import Threes from "./pages/Threes";
import Twos from "./pages/Twos";
import Rbg from "./pages/Rbg";


export default function App() {
    return (
        <BrowserRouter>
            <nav>
                <Link to="/">3s</Link>
                <br />
                <Link to="/2s">2s</Link>
                <br />
                <Link to="/rbg">Rbg</Link>
                <br />
            </nav>
            <DataContextProvider>
                <Routes>
                    <Route path="/" element={<Threes />} />
                    <Route path="/2s" element={<Twos />} />
                    <Route path="/rbg" element={<Rbg />} />
                    <Route path="*" />
                </Routes>
            </DataContextProvider>
        </BrowserRouter>
    );
}
