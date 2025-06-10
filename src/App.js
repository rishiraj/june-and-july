// src/App.js
import React from 'react';
import Dashboard from './components/Dashboard';

function App() {
    return (
        <div>
            {/* You would have a router here for login/registration/dashboard */}
            <Dashboard />
        </div>
    );
}

export default App;
