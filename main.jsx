import { useState } from 'react';
import { createRoot } from 'react-dom/client';
import LandingPage from './src/LandingPage.jsx';
import QuiltLabelMaker from './src/embroidery.jsx';
import ImageEmbroidery from './src/image-embroidery/ImageEmbroidery.jsx';
import LibraryPage from './src/image-embroidery/LibraryPage.jsx';

function App() {
  const [mode, setMode] = useState(null); // null = landing, 'label', 'image', 'library'

  if (mode === 'label')   return <QuiltLabelMaker onBack={() => setMode(null)} />;
  if (mode === 'image')   return <ImageEmbroidery onBack={() => setMode(null)} />;
  if (mode === 'library') return <LibraryPage     onBack={() => setMode(null)} />;
  return <LandingPage onSelect={setMode} />;
}

createRoot(document.getElementById('root')).render(<App />);
