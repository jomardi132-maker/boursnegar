import React from 'react';
import { createRoot } from 'react-dom/client';
import { AppPending } from './AppPending';
import './production.css';
createRoot(document.getElementById('root')!).render(<React.StrictMode><AppPending/></React.StrictMode>);
