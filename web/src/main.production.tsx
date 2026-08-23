import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppProduction } from './AppProduction';
import './stock.css';
import './production.css';
import './modern-theme.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><AppProduction /></React.StrictMode>);
