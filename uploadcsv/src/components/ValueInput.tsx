import React, { ChangeEvent } from 'react';

interface ValueInputProps {
  selectedColumn: string;
  inputValue: string;
  onInputChange: (event: ChangeEvent<HTMLInputElement>) => void;
  onSubmit: () => void;
}

export const ValueInput: React.FC<ValueInputProps> = ({
  selectedColumn,
  inputValue,
  onInputChange,
  onSubmit
}) => {
  return (
    <div style={{ 
      marginTop: '20px',
      padding: '15px',
      border: '1px solid #444',
      borderRadius: '4px',
      backgroundColor: '#222'
    }}>
      <p style={{ marginBottom: '10px', fontWeight: 'bold', color: '#fff' }}>
        Selected Column: {selectedColumn}
      </p>
      <div style={{ display: 'flex', gap: '10px' }}>
        <input
          type="text"
          value={inputValue}
          onChange={onInputChange}
          placeholder="Enter your query..."
          style={{
            padding: '8px',
            borderRadius: '4px',
            border: '1px solid #444',
            backgroundColor: '#333',
            color: '#fff',
            flexGrow: 1
          }}
        />
        <button
          onClick={onSubmit}
          style={{
            padding: '8px 16px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Submit
        </button>
      </div>
    </div>
  );
}; 