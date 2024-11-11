import React from 'react';

interface GoogleSheetsInputProps {
  sheetsLink: string;
  onLinkChange: (link: string) => void;
  onSubmit: () => void;
}

export const GoogleSheetsInput: React.FC<GoogleSheetsInputProps> = ({ 
  sheetsLink, 
  onLinkChange, 
  onSubmit 
}) => {
  return (
    <div style={{ marginBottom: '20px' }}>
      <input
        type="text"
        value={sheetsLink}
        onChange={(e) => onLinkChange(e.target.value)}
        placeholder="Enter Google Sheets URL..."
        style={{
          width: '100%',
          padding: '8px',
          marginBottom: '10px',
          backgroundColor: '#333',
          border: '1px solid #444',
          borderRadius: '4px',
          color: '#fff'
        }}
      />
      <button
        onClick={onSubmit}
        disabled={!sheetsLink}
        style={{
          padding: '8px 16px',
          backgroundColor: sheetsLink ? '#007bff' : '#555',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: sheetsLink ? 'pointer' : 'not-allowed',
          width: '100%'
        }}
      >
        Submit
      </button>
    </div>
  );
}; 