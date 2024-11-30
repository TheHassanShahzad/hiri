import { BrowserRouter } from 'react-router-dom';
import './App.css';
import Navbar from './components/navbar';
import Welcome from './pages/Welcome';
import Stream from './pages/Stream';
import { Routes, Route } from 'react-router-dom';

function App() {
  return (
    <AppContent />
  );
}

function AppContent(){
  return (
    <BrowserRouter>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/live-stream" element={<Stream />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
export default App;
