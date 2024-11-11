import React, { useState, ChangeEvent } from 'react';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuItem } from '@/components/ui/dropdown-menu';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface FileUploadState {
  file: File | null;
  error: string;
  success: string;
  columns: string[];
  selectedColumn: string | null;
  inputValue: string;
  uploadType: 'file' | 'sheets' | null;
  sheetsUrl: string;
}

const CSVUpload: React.FC = () => {
  const [state, setState] = useState<FileUploadState>({
    file: null,
    error: '',
    success: '',
    columns: [],
    selectedColumn: null,
    inputValue: '',
    uploadType: null,
    sheetsUrl: ''
  });

  const [content, setContent] = useState<string | undefined>(undefined);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>): void => {
    setState(prev => ({ 
      ...prev, 
      error: '', 
      success: '', 
      columns: [],
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

  const handleColumnSelect = (column: string) => {
    setState(prev => ({
      ...prev,
      selectedColumn: column
    }));
  };

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setState(prev => ({
      ...prev,
      inputValue: e.target.value
    }));
  };

  const handleSheetsUrlChange = (e: ChangeEvent<HTMLInputElement>) => {
    setState(prev => ({
      ...prev,
      sheetsUrl: e.target.value
    }));
  };

  const handleUploadTypeSelect = (type: 'file' | 'sheets') => {
    setState(prev => ({
      ...prev,
      uploadType: type,
      error: '',
      success: '',
      file: null,
      sheetsUrl: '',
      columns: [],
      selectedColumn: null,
      inputValue: ''
    }));
  };

  const handleSubmit = async () => {
    const { file, selectedColumn, inputValue, uploadType, sheetsUrl } = state;

    if (!selectedColumn || !inputValue) {
      setState(prev => ({
        ...prev,
        error: 'Please select a column and enter a question'
      }));
      return;
    }

    if (uploadType === 'file' && !file) {
      setState(prev => ({
        ...prev,
        error: 'Please select a file'
      }));
      return;
    }

    if (uploadType === 'sheets' && !sheetsUrl) {
      setState(prev => ({
        ...prev,
        error: 'Please enter a Google Sheets URL'
      }));
      return;
    }

    const formData = new FormData();
    if (uploadType === 'file' && file) {
      formData.append('file', file);
    } else if (uploadType === 'sheets') {
      formData.append('sheetsUrl', sheetsUrl);
    }
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

  const handleSheetsUpload = async (): Promise<void> => {
    const { sheetsUrl } = state;
    
    if (!sheetsUrl) {
      setState(prev => ({
        ...prev,
        error: 'Please enter a Google Sheets URL'
      }));
      return;
    }

    try {
      const formData = new FormData();
      formData.append('sheet_url', sheetsUrl);

      const response = await fetch('http://localhost:5001/sheets-headers', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch sheet headers');
      }

      setState(prev => ({
        ...prev,
        columns: data.headers, 
        success: 'Sheet headers loaded successfully!'
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: `Error loading sheet headers: ${err instanceof Error ? err.message : 'Unknown error'}`
      }));
    }
  };

  const { file, error, success, columns, selectedColumn, inputValue } = state;

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>CSV Upload</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-center space-x-4 mb-4">
          <Button
            onClick={() => handleUploadTypeSelect('file')}
            variant={state.uploadType === 'file' ? 'default' : 'secondary'}
          >
            Upload CSV
          </Button>
          <Button
            onClick={() => handleUploadTypeSelect('sheets')}
            variant={state.uploadType === 'sheets' ? 'default' : 'secondary'}
          >
            Use Google Sheets
          </Button>
        </div>

        {state.uploadType === 'file' && (
          <div>
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="w-full border border-gray-300 rounded-md p-2 mb-4"
            />
            <Button onClick={handleUpload} className="w-full">
              Upload
            </Button>
          </div>
        )}

        {state.uploadType === 'sheets' && (
          <div>
            <Input
              type="text"
              placeholder="Enter Google Sheets URL"
              value={state.sheetsUrl}
              onChange={handleSheetsUrlChange}
              className="mb-4"
            />
            <Button onClick={handleSheetsUpload} className="w-full">
              Load Sheet Headers
            </Button>
          </div>
        )}

        {columns.length > 0 && (
          <div className="mb-4">
            <label htmlFor="column-select" className="block mb-2">
              Select a column:
            </label>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  {selectedColumn || 'Select Column'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                {columns.map((column, index) => (
                  <DropdownMenuItem
                    key={index}
                    onClick={() => handleColumnSelect(column)}
                  >
                    {column}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}

        {selectedColumn && (
          <div>
            <label htmlFor="question-input" className="block mb-2">
              Enter a question:
            </label>
            <Input
              id="question-input"
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              className="mb-4"
            />
            <Button onClick={handleSubmit} className="w-full">
              Submit
            </Button>
          </div>
        )}

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert variant="default" className="mb-4">
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {content && (
          <CardFooter>
            <Button onClick={handleDownload} className="w-full">
              Download CSV
            </Button>
          </CardFooter>
        )}
      </CardContent>
    </Card>
  );
};

export default CSVUpload;