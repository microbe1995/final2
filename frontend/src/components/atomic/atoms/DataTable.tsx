import React from 'react';

interface Column {
  key: string;
  label: string;
  align?: 'left' | 'center' | 'right';
  width?: string;
}

interface DataTableProps {
  columns: Column[];
  data: Record<string, any>[];
  className?: string;
  striped?: boolean;
}

const DataTable: React.FC<DataTableProps> = ({
  columns,
  data,
  className = '',
  striped = true,
}) => {
  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className='w-full'>
        <thead>
          <tr className='border-b border-border/30'>
            {columns.map(column => (
              <th
                key={column.key}
                className={`py-2 font-medium text-${column.align || 'left'}`}
                style={{ width: column.width }}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className={`border-b border-border/20 ${
                striped && rowIndex % 2 === 1 ? 'bg-muted/30' : ''
              }`}
            >
              {columns.map(column => (
                <td
                  key={column.key}
                  className={`py-2 text-${column.align || 'left'}`}
                >
                  {row[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
