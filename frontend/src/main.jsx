import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const stricModeOn = false;

function renderApp() {
    if (stricModeOn) {
        return (
            <React.StrictMode>
                <App />
            </React.StrictMode>
        );
    }
    return (
        <App />
    );
}

ReactDOM.createRoot(document.getElementById('root')).render(renderApp());
