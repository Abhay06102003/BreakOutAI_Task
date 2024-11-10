import React, { ChangeEvent } from 'react';

interface FileUploadProps {
  file: File | null;
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onUpload: () => void;
}

export const FileUploadSection: React.FC<FileUploadProps> = ({ file, onFileChange, onUpload }) => {
  return (
    <div>
      <label htmlFor="csv-upload" style={{ display: 'block', marginBottom: '10px' }}>
        Upload CSV File
      </label>
      
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          id="csv-upload"
          type="file"
          accept=".csv"
          onChange={onFileChange}
          style={{ marginBottom: '10px', color: '#fff' }}
        />
        
        <button 
          onClick={onUpload}
          disabled={!file}
          style={{
            padding: '8px 16px',
            backgroundColor: !file ? '#555' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: file ? 'pointer' : 'not-allowed'
          }}
        >
          Upload
        </button>
      </div>
      
      {file && (
        <p style={{ fontSize: '14px', color: '#bbb' }}>
          Selected: {file.name}
        </p>
      )}
    </div>
  );
}; 