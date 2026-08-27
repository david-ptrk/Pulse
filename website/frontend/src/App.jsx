import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Architecture from './pages/Architecture'
import OnlineEditor from "./pages/OnlineEditor";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/architecture" element={<Architecture />} />
      <Route path="/editor" element={<OnlineEditor />} />
    </Routes>
  )
}

export default App
