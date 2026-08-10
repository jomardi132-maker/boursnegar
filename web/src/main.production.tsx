import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppProduction } from './AppProduction';
import './production.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><AppProduction /></React.StrictMode>);
