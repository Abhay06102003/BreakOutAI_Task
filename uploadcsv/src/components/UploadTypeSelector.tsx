import React from 'react';

interface UploadTypeSelectorProps {
  uploadType: 'csv' | 'sheets';
  onTypeChange: (type: 'csv' | 'sheets') => void;
}

export const UploadTypeSelector: React.FC<UploadTypeSelectorProps> = ({ uploadType, onTypeChange }) => {
  return (
    <div style={{ marginBottom: '20px' }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        <button
          onClick={() => onTypeChange('csv')}
          style={{
            padding: '8px 16px',
            backgroundColor: uploadType === 'csv' ? '#007bff' : '#444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            flex: 1
          }}
        >
          CSV Upload
        </button>
        <button
          onClick={() => onTypeChange('sheets')}
          style={{
            padding: '8px 16px',
            backgroundColor: uploadType === 'sheets' ? '#007bff' : '#444',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            flex: 1
          }}
        >
          Google Sheets
        </button>
      </div>
    </div>
  );
}; 