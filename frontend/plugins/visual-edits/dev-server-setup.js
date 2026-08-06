/**
 * Dev Server Setup for Visual Edits Plugin
 * 
 * This module configures the development server with hot reload
 * and visual editing capabilities.
 */

const path = require('path');
const fs = require('fs');

class DevServerSetup {
  constructor(options = {}) {
    this.options = {
      port: options.port || 3001,
      hotReload: options.hotReload !== false,
      visualEdit: options.visualEdit !== false,
      watchPaths: options.watchPaths || ['./src', './components'],
      ...options
    };
    
    this.watcher = null;
    this.connections = new Set();
  }

  /**
   * Initialize the development server
   */
  init() {
    console.log('Initializing dev server setup...');
    
    if (this.options.hotReload) {
      this.setupHotReload();
    }
    
    if (this.options.visualEdit) {
      this.setupVisualEdit();
    }
    
    console.log('Dev server setup complete');
  }

  /**
   * Setup hot reload functionality
   */
  setupHotReload() {
    console.log('Setting up hot reload...');
    
    const chokidar = require('chokidar');
    
    this.watcher = chokidar.watch(this.options.watchPaths, {
      ignored: /node_modules/,
      persistent: true,
      ignoreInitial: true
    });
    
    this.watcher.on('change', (filePath) => {
      console.log(`File changed: ${filePath}`);
      this.broadcast({
        type: 'reload',
        file: filePath,
        timestamp: Date.now()
      });
    });
    
    this.watcher.on('add', (filePath) => {
      console.log(`File added: ${filePath}`);
      this.broadcast({
        type: 'add',
        file: filePath,
        timestamp: Date.now()
      });
    });
    
    console.log('Hot reload setup complete');
  }

  /**
   * Setup visual editing capabilities
   */
  setupVisualEdit() {
    console.log('Setting up visual editing...');
    
    // Initialize visual edit overlay
    this.visualEditState = {
      enabled: false,
      selectedElement: null,
      editMode: 'inspect',
      history: []
    };
    
    console.log('Visual editing setup complete');
  }

  /**
   * Broadcast message to all connected clients
   */
  broadcast(message) {
    const messageStr = JSON.stringify(message);
    
    this.connections.forEach(connection => {
      try {
        connection.send(messageStr);
      } catch (error) {
        console.error('Failed to send message:', error);
        this.connections.delete(connection);
      }
    });
  }

  /**
   * Handle new WebSocket connection
   */
  handleConnection(ws) {
    this.connections.add(ws);
    
    ws.on('message', (message) => {
      try {
        const data = JSON.parse(message);
        this.handleMessage(data, ws);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    });
    
    ws.on('close', () => {
      this.connections.delete(ws);
    });
    
    // Send initial state
    ws.send(JSON.stringify({
      type: 'init',
      state: this.visualEditState
    }));
  }

  /**
   * Handle incoming message
   */
  handleMessage(data, ws) {
    switch (data.type) {
      case 'edit':
        this.handleEdit(data);
        break;
      case 'inspect':
        this.handleInspect(data);
        break;
      case 'save':
        this.handleSave(data);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  /**
   * Handle edit operation
   */
  handleEdit(data) {
    console.log('Processing edit:', data);
    
    // Apply edit to file
    const { filePath, changes } = data;
    
    try {
      let content = fs.readFileSync(filePath, 'utf8');
      
      changes.forEach(change => {
        content = content.replace(change.oldValue, change.newValue);
      });
      
      fs.writeFileSync(filePath, content);
      
      this.broadcast({
        type: 'edit-applied',
        file: filePath,
        timestamp: Date.now()
      });
    } catch (error) {
      console.error('Failed to apply edit:', error);
    }
  }

  /**
   * Handle inspect operation
   */
  handleInspect(data) {
    console.log('Processing inspect:', data);
    
    // Return element information
    const { selector } = data;
    
    this.broadcast({
      type: 'inspect-result',
      selector,
      info: {
        file: 'unknown',
        line: 0,
        component: 'unknown'
      }
    });
  }

  /**
   * Handle save operation
   */
  handleSave(data) {
    console.log('Processing save:', data);
    
    // Save all pending changes
    this.broadcast({
      type: 'saved',
      timestamp: Date.now()
    });
  }

  /**
   * Cleanup resources
   */
  destroy() {
    if (this.watcher) {
      this.watcher.close();
    }
    
    this.connections.clear();
    
    console.log('Dev server setup destroyed');
  }
}

module.exports = DevServerSetup;
