//import { useState } from 'react'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from './pages/auth/login/Login.tsx'
import SignUp from './pages/auth/signup/SignUp.tsx'
import './App.css'
import Dashboard from "./pages/dashboard/Dashboard.tsx";

function App() {
  return (
    <>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App
