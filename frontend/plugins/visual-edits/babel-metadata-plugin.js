/**
 * Babel Metadata Plugin for Visual Edits
 * 
 * This Babel plugin injects metadata into JSX elements to enable
 * visual editing and component inspection.
 */

module.exports = function(babel) {
  const { types: t } = babel;
  
  return {
    name: 'babel-metadata-plugin',
    visitor: {
      JSXOpeningElement(path, state) {
        const filename = state.file.opts.filename || 'unknown';
        const loc = path.node.loc;
        
        if (!loc) return;
        
        // Create metadata attributes
        const metadata = {
          'data-source-file': filename,
          'data-line-number': loc.start.line,
          'data-column-number': loc.start.column,
          'data-component': path.node.name.name || 'unknown'
        };
        
        // Add data attributes to JSX element
        Object.entries(metadata).forEach(([key, value]) => {
          // Check if attribute already exists
          const exists = path.node.attributes.some(
            attr => attr.type === 'JSXAttribute' && attr.name.name === key
          );
          
          if (!exists) {
            const attribute = t.jsxAttribute(
              t.jsxIdentifier(key),
              t.stringLiteral(String(value))
            );
            path.node.attributes.push(attribute);
          }
        });
      },
      
      FunctionDeclaration(path, state) {
        // Add displayName to components for better debugging
        const filename = state.file.opts.filename || 'unknown';
        
        if (
          path.node.id &&
          path.node.id.name &&
          (path.node.id.name.match(/^[A-Z]/) || path.node.id.name.includes('Component'))
        ) {
          const displayName = t.assignmentExpression(
            '=',
            t.memberExpression(
              t.identifier(path.node.id.name),
              t.identifier('displayName')
            ),
            t.stringLiteral(path.node.id.name)
          );
          
          // Insert after function declaration
          path.insertAfter(t.expressionStatement(displayName));
        }
      },
      
      ArrowFunctionExpression(path, state) {
        // Handle arrow function components
        const parent = path.parent;
        
        if (
          parent.type === 'VariableDeclarator' &&
          parent.id &&
          parent.id.name &&
          parent.id.name.match(/^[A-Z]/)
        ) {
          // This is likely a component
          const componentName = parent.id.name;
          
          // We can't easily add displayName to arrow functions
          // without wrapping them, so we just note it
          if (state.opts && state.opts.verbose) {
            console.log(`Found arrow component: ${componentName}`);
          }
        }
      }
    }
  };
};
