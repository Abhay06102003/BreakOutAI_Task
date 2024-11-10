import './App.css'
import CSVUpload from './components/CSVUpload.tsx'

function App() {
  const appStyles = {
    backgroundColor: '#121212',
    color: '#e0e0e0',
    minHeight: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontFamily: 'Arial, sans-serif'
  }

  return (
    <div style={appStyles}>
      <CSVUpload />
    </div>
  )
}

export default App
