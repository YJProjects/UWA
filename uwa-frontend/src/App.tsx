//import { useState } from 'react'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from './components/auth/login/Login.tsx'
import SignUp from './components/auth/signup/SignUp.tsx'
import './App.css'

function App() {
  return (
    <>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App
