import React, { useState } from 'react';
import UploadComponent from './components/Upload';
import './App.css';

function App() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [improvements, setImprovements] = useState("");
  const [loading, setLoading] = useState(false);
  const [length, setLength] = useState("medium");

  const handleUpload = async (file) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("length", length);

      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setUploadedFile(result);
        setSummary(result.summary);
        setImprovements(result.improvements);
      } else {
        alert(`Error: ${result.detail}`);
      }
    } catch (error) {
      alert("Upload failed. Check console for details.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Document Summary Assistant</h1>
      
      <UploadComponent
        onUpload={handleUpload}
        length={length}
        setLength={setLength}
        loading={loading}
        uploadedFile={uploadedFile}
        summary={summary}
        improvements={improvements}
      />
    </div>
  );
}

useEffect(() => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    setIsDarkMode(savedTheme === 'dark');
  }
}, []);


const toggleTheme = () => {
  const newTheme = !isDarkMode;
  setIsDarkMode(newTheme);
  localStorage.setItem('theme', newTheme ? 'dark' : 'light');
};

export default App;