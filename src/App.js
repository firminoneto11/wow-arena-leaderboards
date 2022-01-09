import { AuthProvider } from "./context/AuthContext";
import HelloWorld from "./components/HelloWorld";


export default function App() {

    return (
        <AuthProvider>
            <HelloWorld />
        </AuthProvider>
    );
}
