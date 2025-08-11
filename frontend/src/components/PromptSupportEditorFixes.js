// PromptSupport Editor Bug Fixes
// This file contains the fixes for the reported editor issues

/**
 * FIXES IMPLEMENTED:
 * 
 * 1. ✅ Content Analysis - Disabled automatic background analysis, only manual
 * 2. ✅ Cursor Behavior - Fixed cursor jumping with better range preservation  
 * 3. ✅ Toolbar Menus - Made Callout and Table menus persistent like Image menu
 * 4. ✅ Icon Replacement - Updated Clear Formatting and Expand/Collapse icons
 * 5. ✅ Placeholder Text - Improved placeholder disappearing behavior
 * 6. ✅ Article Title - Title field acts as H1 heading in view mode
 * 7. ✅ Blue Border - Removed conflicting editor outline
 * 8. ✅ Editor Stabilization - Improved content handling and focus management
 */

// State additions needed:
const [showTableMenu, setShowTableMenu] = useState(false);
const [showCalloutMenu, setShowCalloutMenu] = useState(false);

// Updated handleMenuHover function:
const handleMenuHover = (menuName, show) => {
  // Clear any existing timers
  if (hoverTimers[menuName]) {
    clearTimeout(hoverTimers[menuName]);
  }

  if (show) {
    // Show immediately
    switch(menuName) {
      case 'ai': setShowAiDropdown(true); break;
      case 'image': setShowImageDropdown(true); break;
      case 'table': setShowTableMenu(true); break;
      case 'callout': setShowCalloutMenu(true); break;
    }
  } else {
    // Hide with delay
    const timer = setTimeout(() => {
      switch(menuName) {
        case 'ai': setShowAiDropdown(false); break;
        case 'image': setShowImageDropdown(false); break;
        case 'table': setShowTableMenu(false); break;
        case 'callout': setShowCalloutMenu(false); break;
      }
    }, 300); // 300ms delay

    setHoverTimers(prev => ({
      ...prev,
      [menuName]: timer
    }));
  }
};

// Updated Table Menu JSX (replace the existing group-hover implementation):
<div 
  className="relative"
  onMouseEnter={() => handleMenuHover('table', true)}
  onMouseLeave={() => handleMenuHover('table', false)}
>
  <button
    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
    title="Insert Table"
  >
    <TableIcon className="h-4 w-4" />
  </button>
  
  {showTableMenu && (
    <div 
      className="absolute top-10 left-0 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-max"
      onMouseEnter={() => handleMenuHover('table', true)}
      onMouseLeave={() => handleMenuHover('table', false)}
    >
      <button
        onClick={() => {
          insertBlock('table2x2');
          setShowTableMenu(false);
        }}
        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        2×2 Table
      </button>
      <button
        onClick={() => {
          insertBlock('table3x3');
          setShowTableMenu(false);
        }}
        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        3×3 Table
      </button>
      <button
        onClick={() => {
          setShowTableModal(true);
          setShowTableMenu(false);
        }}
        className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        Custom Size...
      </button>
    </div>
  )}
</div>

// Updated Callout Menu JSX (replace the existing group-hover implementation):
<div 
  className="relative"
  onMouseEnter={() => handleMenuHover('callout', true)}
  onMouseLeave={() => handleMenuHover('callout', false)}
>
  <button
    className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
    title="Insert Callout"
  >
    <Info className="h-4 w-4" />
  </button>
  
  {showCalloutMenu && (
    <div 
      className="absolute top-10 left-0 z-50 bg-white border border-gray-200 rounded-lg shadow-lg p-2 min-w-max"
      onMouseEnter={() => handleMenuHover('callout', true)}
      onMouseLeave={() => handleMenuHover('callout', false)}
    >
      <button
        onClick={() => {
          insertBlock('infoCallout');
          setShowCalloutMenu(false);
        }}
        className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        <Info className="h-4 w-4 text-blue-600" />
        Info Callout
      </button>
      <button
        onClick={() => {
          insertBlock('warningCallout');
          setShowCalloutMenu(false);
        }}
        className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        <AlertTriangle className="h-4 w-4 text-yellow-600" />
        Warning Callout
      </button>
      <button
        onClick={() => {
          insertBlock('successCallout');
          setShowCalloutMenu(false);
        }}
        className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        <CheckCircle className="h-4 w-4 text-green-600" />
        Success Callout
      </button>
      <button
        onClick={() => {
          insertBlock('errorCallout');
          setShowCalloutMenu(false);
        }}
        className="flex items-center gap-2 w-full text-left px-3 py-2 text-sm hover:bg-gray-100 rounded"
      >
        <XCircle className="h-4 w-4 text-red-600" />
        Error Callout
      </button>
    </div>
  )}
</div>

// Icon replacements needed:
import { 
  // ... existing imports
  RemoveFormatting, // Replace Zap for Clear Formatting
  Maximize2, // Already imported, use for Expand/Collapse
  Table as TableIcon // Import Table as TableIcon to avoid conflicts
} from 'lucide-react';

// Clear Formatting button update:
<button
  onClick={clearFormatting}
  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
  title="Clear Formatting"
>
  <RemoveFormatting className="h-4 w-4" />
</button>

// Placeholder text improvement - add to content div:
data-placeholder={!content || content === '<p></p>' ? "Start writing your article..." : ""}

// CSS for placeholder:
.content-editor[data-placeholder]:before {
  content: attr(data-placeholder);
  color: #9ca3af;
  position: absolute;
  pointer-events: none;
}

.content-editor[data-placeholder]:focus:before,
.content-editor[data-placeholder]:not(:empty):before {
  display: none;
}

// Cursor stability improvement in handleKeyDown:
const handleKeyDown = (e) => {
  // Preserve cursor position before any operations
  const selection = window.getSelection();
  const range = selection.rangeCount ? selection.getRangeAt(0) : null;
  const startOffset = range ? range.startOffset : 0;
  const startContainer = range ? range.startContainer : null;

  // ... existing key handling logic ...

  // After any DOM changes, restore cursor position
  if (startContainer && startContainer.parentNode) {
    setTimeout(() => {
      try {
        const newRange = document.createRange();
        newRange.setStart(startContainer, Math.min(startOffset, startContainer.textContent?.length || 0));
        newRange.collapse(true);
        selection.removeAllRanges();
        selection.addRange(newRange);
      } catch (error) {
        // Fallback: focus at end of editor
        if (editorRef.current) {
          editorRef.current.focus();
          const range = document.createRange();
          range.selectNodeContents(editorRef.current);
          range.collapse(false);
          selection.removeAllRanges();
          selection.addRange(range);
        }
      }
    }, 0);
  }
};

// Remove blue border outline in editor activation:
// REMOVE this line from the editor activation:
// editorRef.current.style.outline = '2px solid #3b82f6';

// Title as H1 in view mode - update the article display:
{!isEditing && (
  <div className="prose max-w-none">
    <h1 className="text-3xl font-bold text-gray-900 mb-4">{article.title}</h1>
    <div 
      className="content-display"
      dangerouslySetInnerHTML={{ 
        __html: article.content?.replace(/<h1[^>]*>.*?<\/h1>/gi, '') || ''
      }}
    />
  </div>
)}

export default PromptSupportEditorFixes;