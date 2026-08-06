import React from 'react';
import { Printer } from 'lucide-react';

const PrintButton = ({ className = '' }) => {
  const handlePrint = () => {
    window.print();
  };

  return (
    <button
      onClick={handlePrint}
      className={`inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 print:hidden ${className}`}
      title="Print this page"
    >
      <Printer className="w-4 h-4 mr-2" />
      Print
    </button>
  );
};

export default PrintButton;
