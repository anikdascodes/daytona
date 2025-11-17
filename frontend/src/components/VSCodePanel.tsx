import React from 'react';

export const VSCodePanel: React.FC = () => {
  // VS Code server URL from nginx proxy
  const vscodeUrl = '/vscode';

  return (
    <div className="w-3/5 h-full bg-gray-800 border-r border-gray-700">
      <div className="h-full flex flex-col">
        <div className="bg-gray-700 px-4 py-2 text-sm border-b border-gray-600">
          <span className="font-medium">📝 VS Code</span>
        </div>
        <iframe
          src={vscodeUrl}
          className="flex-1 w-full border-0"
          title="VS Code"
          sandbox="allow-same-origin allow-scripts allow-forms allow-modals allow-popups"
        />
      </div>
    </div>
  );
};
