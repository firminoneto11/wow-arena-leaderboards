import { AuthProvider } from "./context/AuthContext";
import { BrowserRouter, Route } from "react-router-dom";
import TwosLadder from './pages/2v2Page';
import ThreesLadder from './pages/3v3Page';
import RBGLadder from './pages/RBGPage';
import { Fragment } from "react";


export default function App() {

    return (
        <Fragment>
            <BrowserRouter>
                <AuthProvider>
                    <Route path={"/"} exact component={ThreesLadder} />
                    <Route path={"/2v2"} exact component={TwosLadder} />
                    <Route path={"/rbg"} exact component={RBGLadder} />
                </AuthProvider>
            </BrowserRouter>
        </Fragment>
    );
}
