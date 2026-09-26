import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Architecture from './pages/Architecture';
import OnlineEditor from "./pages/OnlineEditor";
import About from "./pages/About";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/architecture" element={<Architecture />} />
      <Route path="/editor" element={<OnlineEditor />} />
      <Route path="/about" element={<About />} />
    </Routes>
  )
}

export default App
