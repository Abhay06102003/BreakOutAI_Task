interface ColumnDropdownProps {
  columns: string[];
  isOpen: boolean;
  onToggle: () => void;
  onSelect: (column: string) => void;
}

export const ColumnDropdown: React.FC<ColumnDropdownProps> = ({ 
  columns, 
  isOpen, 
  onToggle, 
  onSelect 
}) => {
  return (
    <div style={{ position: 'relative', marginTop: '20px' }}>
      <button
        onClick={onToggle}
        style={{
          padding: '8px 16px',
          backgroundColor: '#444',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}
      >
        View Columns
        <span style={{ 
          transform: isOpen ? 'rotate(180deg)' : 'none',
          transition: 'transform 0.3s ease'
        }}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: '0',
          right: '0',
          backgroundColor: '#222',
          border: '1px solid #444',
          borderRadius: '4px',
          marginTop: '4px',
          boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
          zIndex: 1000,
          maxHeight: '200px',
          overflowY: 'auto'
        }}>
          <ul style={{ listStyle: 'none', padding: '0', margin: '0' }}>
            {columns.map((column, index) => (
              <li 
                key={index}
                style={{ 
                  padding: '8px 16px',
                  borderBottom: index < columns.length - 1 ? '1px solid #444' : 'none',
                  cursor: 'pointer',
                  color: '#fff'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#555';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#222';
                }}
                onClick={() => onSelect(column)}
              >
                {column}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}; 