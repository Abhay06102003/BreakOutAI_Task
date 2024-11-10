import React, { useState, ChangeEvent } from 'react';
import { FileUploadSection } from './FileUploadSection';
import { ColumnDropdown } from './ColumnDropdown';
import { ValueInput } from './ValueInput';

interface FileUploadState {
  file: File | null;
  error: string;
  success: string;
  columns: string[];
  isDropdownOpen: boolean;
  selectedColumn: string | null;
  inputValue: string;
}

const CSVUpload: React.FC = () => {
  const [state, setState] = useState<FileUploadState>({
    file: null,
    error: '',
    success: '',
    columns: [],
    isDropdownOpen: false,
    selectedColumn: null,
    inputValue: ''
  });

  const [content, setContent] = useState<string | undefined>(undefined);


  const handleFileChange = (event: ChangeEvent<HTMLInputElement>): void => {
    setState(prev => ({ 
      ...prev, 
      error: '', 
      success: '', 
      columns: [],
      isDropdownOpen: false,
      selectedColumn: null,
      inputValue: ''
    }));
    
    const selectedFile = event.target.files?.[0];
    
    if (selectedFile) {
      const isCSVByExtension = selectedFile.name.toLowerCase().endsWith('.csv');
      const isCSVByType = selectedFile.type === 'text/csv';
      
      if (!isCSVByExtension && !isCSVByType) {
        setState(prev => ({
          ...prev,
          file: null,
          error: 'Please upload only CSV files'
        }));
        return;
      }
      
      setState(prev => ({
        ...prev,
        file: selectedFile,
        success: `File "${selectedFile.name}" selected successfully`
      }));

      readColumnNames(selectedFile);
    }
  };

  const readColumnNames = (file: File): void => {
    const reader = new FileReader();
    
    reader.onload = (e: ProgressEvent<FileReader>) => {
      const text = e.target?.result as string;
      if (text) {
        const firstLine = text.split('\n')[0];
        const columns = firstLine
          .split(',')
          .map(column => column.trim().replace(/"/g, ''));
        
        setState(prev => ({
          ...prev,
          columns
        }));
      }
    };

    reader.onerror = () => {
      setState(prev => ({
        ...prev,
        error: 'Error reading file headers'
      }));
    };

    reader.readAsText(file);
  };

  const handleUpload = async (): Promise<void> => {
    const { file } = state;
    
    if (!file) {
      setState(prev => ({
        ...prev,
        error: 'Please select a file first'
      }));
      return;
    }

    try {
      const reader = new FileReader();
      
      reader.onload = (e: ProgressEvent<FileReader>) => {
        const text = e.target?.result as string;
        const rows = text.split('\n');
        const headers = rows[0].split(',').map(header => header.trim().replace(/"/g, ''));
        console.log('Full file content - First row (headers):', headers);
        console.log('Number of columns:', headers.length);
        
        setState(prev => ({
          ...prev,
          success: 'File uploaded successfully!'
        }));
      };

      reader.onerror = () => {
        throw new Error('Error reading file');
      };

      reader.readAsText(file);
      
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: `Error uploading file: ${err instanceof Error ? err.message : 'Unknown error'}`
      }));
    }
  };

  const toggleDropdown = () => {
    setState(prev => ({
      ...prev,
      isDropdownOpen: !prev.isDropdownOpen
    }));
  };

  const handleColumnSelect = (column: string) => {
    setState(prev => ({
      ...prev,
      selectedColumn: column,
      isDropdownOpen: false
    }));
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setState(prev => ({
      ...prev,
      inputValue: e.target.value
    }));
  };

  const handleSubmit = async () => {
    const { file, selectedColumn, inputValue } = state;
    
    if (!file || !selectedColumn || !inputValue) {
      setState(prev => ({
        ...prev,
        error: 'Please select a file, column, and enter a question'
      }));
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('column', selectedColumn);
    formData.append('question', inputValue);

    try {
      setState(prev => ({ ...prev, error: '', success: 'Processing...' }));
      
      const response = await fetch('http://localhost:5001/process', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process file');
      }

      setContent(data.data);

      setState(prev => ({
        ...prev,
        success: 'File processed successfully!',
        selectedColumn: null,
        inputValue: ''
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: `Error processing file: ${err instanceof Error ? err.message : 'Unknown error'}`,
        success: ''
      }));
    }
  };

  const handleDownload = () => {
    if (!content) return;
  
    // Create a Blob from the CSV content
    const blob = new Blob([content], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
  
    // Create a temporary anchor element and trigger a download
    const link = document.createElement('a');
    link.href = url;
    link.download = 'data.csv';
    document.body.appendChild(link);
    link.click();
  
    // Clean up the URL object and remove the link element
    URL.revokeObjectURL(url);
    document.body.removeChild(link);
  };
  

  const { file, error, success, columns, isDropdownOpen, selectedColumn, inputValue } = state;

  return (
    <div style={{ maxWidth: '500px', margin: '20px auto', padding: '20px', backgroundColor: '#333', color: '#fff', borderRadius: '8px' }}>
      <FileUploadSection
        file={file}
        onFileChange={handleFileChange}
        onUpload={handleUpload}
      />

      {columns.length > 0 && success && (
        <ColumnDropdown
          columns={columns}
          isOpen={isDropdownOpen}
          onToggle={toggleDropdown}
          onSelect={handleColumnSelect}
        />
      )}

      {selectedColumn && (
        <ValueInput
          selectedColumn={selectedColumn}
          inputValue={inputValue}
          onInputChange={handleInputChange}
          onSubmit={handleSubmit}
        />
      )}

      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#ff4d4d', 
          color: '#fff', 
          borderRadius: '4px',
          marginTop: '10px' 
        }}>
          {error}
        </div>
      )}

      {success && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#28a745', 
          color: '#fff', 
          borderRadius: '4px',
          marginTop: '10px' 
        }}>
          {success}
        </div>
      )}

      {content && (
        <button onClick={handleDownload}>
          download
        </button>
      )}
    </div>
  );
};

export default CSVUpload;
