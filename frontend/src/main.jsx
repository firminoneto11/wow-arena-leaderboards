import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const strictMode = false;

function renderApp() {
    if (strictMode) {
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
