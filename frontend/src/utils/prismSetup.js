/**
 * Prism.js Setup for PromptSupport V2 Engine
 * Handles syntax highlighting, line numbers, copy-to-clipboard, and normalization
 */

// Core Prism imports
import Prism from 'prismjs';

// Core CSS styles - using the default prism theme
import 'prismjs/themes/prism.css';

// Plugin CSS imports
import 'prismjs/plugins/line-numbers/prism-line-numbers.css';
import 'prismjs/plugins/toolbar/prism-toolbar.css';

// Language components - matching V2CodeNormalizationSystem backend
import 'prismjs/components/prism-bash';
import 'prismjs/components/prism-json';
import 'prismjs/components/prism-yaml';
import 'prismjs/components/prism-xml-doc';
import 'prismjs/components/prism-graphql';
import 'prismjs/components/prism-sql';
import 'prismjs/components/prism-javascript';
import 'prismjs/components/prism-typescript';
import 'prismjs/components/prism-python';
import 'prismjs/components/prism-css';
import 'prismjs/components/prism-markup-templating';

// Plugin imports
import 'prismjs/plugins/line-numbers/prism-line-numbers';
import 'prismjs/plugins/toolbar/prism-toolbar';
import 'prismjs/plugins/normalize-whitespace/prism-normalize-whitespace';
import 'prismjs/plugins/copy-to-clipboard/prism-copy-to-clipboard';

class PrismManager {
  constructor() {
    this.initialized = false;
    this.observer = null;
  }

  /**
   * Initialize Prism with default configuration
   */
  init() {
    if (this.initialized) {
      console.log('🎨 Prism already initialized');
      return;
    }

    console.log('🎨 Initializing Prism.js for V2 Engine code blocks');

    // Configure normalize whitespace plugin
    if (Prism.plugins && Prism.plugins.NormalizeWhitespace) {
      Prism.plugins.NormalizeWhitespace.setDefaults({
        'remove-trailing': true,
        'remove-indent': true,
        'left-trim': true,
        'right-trim': true,
        'tabs-to-spaces': 2,
        'break-lines': false,
        'indent': 0,
        'remove-initial-line-feed': true,
        'spaces-to-tabs': 0
      });
      console.log('✅ Prism whitespace normalization configured');
    }

    // Configure toolbar plugin for accessibility
    if (Prism.plugins && Prism.plugins.toolbar) {
      // Custom copy button with better accessibility
      Prism.plugins.toolbar.registerButton('copy-to-clipboard', function(env) {
        const button = document.createElement('button');
        button.textContent = 'Copy';
        button.className = 'prism-copy-button';
        button.setAttribute('aria-label', 'Copy code to clipboard');
        button.setAttribute('type', 'button');
        
        // Enhanced copy functionality
        button.addEventListener('click', function() {
          const code = env.code;
          
          if (navigator.clipboard) {
            navigator.clipboard.writeText(code).then(() => {
              button.textContent = 'Copied!';
              setTimeout(() => {
                button.textContent = 'Copy';
              }, 2000);
            }).catch(() => {
              this.fallbackCopy(code, button);
            });
          } else {
            this.fallbackCopy(code, button);
          }
        });

        return button;
      });
      console.log('✅ Prism toolbar with copy button configured');
    }

    // Initial highlighting of existing content
    this.highlightAll();

    // Set up mutation observer for dynamic content
    this.setupMutationObserver();

    this.initialized = true;
    console.log('✅ Prism.js initialization complete');
  }

  /**
   * Fallback copy method for browsers without clipboard API
   */
  fallbackCopy(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
      const result = document.execCommand('copy');
      if (result) {
        button.textContent = 'Copied!';
        setTimeout(() => {
          button.textContent = 'Copy';
        }, 2000);
      }
    } catch (err) {
      console.error('Copy failed:', err);
      button.textContent = 'Copy failed';
      setTimeout(() => {
        button.textContent = 'Copy';
      }, 2000);
    } finally {
      document.body.removeChild(textArea);
    }
  }

  /**
   * Highlight all code blocks in the document
   */
  highlightAll() {
    if (typeof Prism !== 'undefined') {
      Prism.highlightAll();
      console.log('🎨 Prism highlighted all code blocks');
    }
  }

  /**
   * Highlight code blocks within a specific container
   */
  highlightAllUnder(container) {
    if (typeof Prism !== 'undefined' && container) {
      Prism.highlightAllUnder(container);
      console.log('🎨 Prism highlighted code blocks in container');
    }
  }

  /**
   * Setup mutation observer to watch for new code blocks
   */
  setupMutationObserver() {
    if (!window.MutationObserver) return;

    // Disconnect existing observer
    if (this.observer) {
      this.observer.disconnect();
    }

    this.observer = new MutationObserver((mutations) => {
      let shouldHighlight = false;

      mutations.forEach((mutation) => {
        if (mutation.type === 'childList') {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === 1) { // Element node
              // Check if added node contains code blocks
              if (node.matches && 
                  (node.matches('pre[class*="language-"]') || 
                   node.matches('code[class*="language-"]') ||
                   node.querySelector('pre[class*="language-"], code[class*="language-"]'))) {
                shouldHighlight = true;
              }
            }
          });
        }
      });

      if (shouldHighlight) {
        // Debounce highlighting to avoid excessive calls
        clearTimeout(this.highlightTimeout);
        this.highlightTimeout = setTimeout(() => {
          this.highlightAll();
        }, 100);
      }
    });

    this.observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    console.log('✅ Prism mutation observer setup complete');
  }

  /**
   * Manually highlight a specific element
   */
  highlightElement(element) {
    if (typeof Prism !== 'undefined' && element) {
      Prism.highlightElement(element);
    }
  }

  /**
   * Re-initialize Prism (useful for dynamic content updates)
   */
  reinitialize() {
    console.log('🔄 Reinitializing Prism...');
    this.initialized = false;
    this.init();
  }

  /**
   * Clean up resources
   */
  destroy() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    clearTimeout(this.highlightTimeout);
    this.initialized = false;
    console.log('🗑️ Prism cleanup complete');
  }
}

// Create singleton instance
const prismManager = new PrismManager();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    prismManager.init();
  });
} else {
  // DOM is already ready
  prismManager.init();
}

export default prismManager;
export { Prism };