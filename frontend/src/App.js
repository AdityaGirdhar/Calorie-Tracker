import React from 'react';
import Navbar from './Components/Navbar';
import Main from './Components/Main';
import About from './Components/About';
import {
  Route,
  Routes,
  BrowserRouter
} from "react-router-dom";

function App() {
  return (
    <>
      <BrowserRouter>
      <Navbar title="Focus" />
        <Routes>
          <Route path="/" element={<Main/>} />
          <Route path="/about" element={<About/>} />
          <Route path="/pricing" element={<></>} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;


