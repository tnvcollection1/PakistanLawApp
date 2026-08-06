import React from 'react';
import CaseSearchBox from '../components/CaseSearchBox';
import SidebarLayout from '../components/SidebarLayout';

function App() {
  return (
    <SidebarLayout>
      <div className="space-y-6">
        <CaseSearchBox />
      </div>
    </SidebarLayout>
  );
}

export default App;
