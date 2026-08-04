//import { useState } from 'react'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from './pages/auth/login/Login.tsx'
import SignUp from './pages/auth/signup/SignUp.tsx'
import './App.css'
import DashboardLayout from "./components/dashboard/DashboardLayout.tsx";
import OverviewPage from "./pages/dashboard/overview/OverviewPage.tsx";
import CoursesPage from "./pages/dashboard/courses/CoursesPage.tsx";
import SettingsPage from "./pages/dashboard/settings/SettingsPage.tsx";
import HelpPage from "./pages/dashboard/help/HelpPage.tsx";

function App() {
  return (
    <>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route index element={<OverviewPage />} />
          <Route path="courses" element={<CoursesPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="help" element={<HelpPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App
