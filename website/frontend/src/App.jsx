import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Architecture from './pages/Architecture'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/architecture" element={<Architecture />} />
    </Routes>
  )
}

export default App
