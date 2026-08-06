/**
 * Utility for Server-Sent Events (SSE) connection management
 */

export class SSEConnection {
  constructor(url, options = {}) {
    this.url = url;
    this.options = {
      onMessage: () => {},
      onError: () => {},
      onOpen: () => {},
      onClose: () => {},
      reconnectInterval: 5000,
      maxReconnects: 5,
      ...options,
    };
    
    this.eventSource = null;
    this.reconnectCount = 0;
    this.reconnectTimer = null;
    this.isIntentionallyClosed = false;
  }
  
  connect() {
    if (this.eventSource) {
      return;
    }
    
    this.isIntentionallyClosed = false;
    
    try {
      this.eventSource = new EventSource(this.url);
      
      this.eventSource.onopen = () => {
        console.log('SSE connection opened');
        this.reconnectCount = 0;
        this.options.onOpen();
      };
      
      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.options.onMessage(data);
        } catch (e) {
          this.options.onMessage(event.data);
        }
      };
      
      this.eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        this.options.onError(error);
        
        if (!this.isIntentionallyClosed) {
          this.reconnect();
        }
      };
    } catch (error) {
      console.error('Failed to create SSE connection:', error);
      this.options.onError(error);
    }
  }
  
  reconnect() {
    if (this.reconnectCount >= this.options.maxReconnects) {
      console.error('Max reconnects reached');
      return;
    }
    
    this.reconnectCount++;
    console.log(`Reconnecting... Attempt ${this.reconnectCount}/${this.options.maxReconnects}`);
    
    this.disconnect();
    
    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, this.options.reconnectInterval);
  }
  
  disconnect() {
    this.isIntentionallyClosed = true;
    
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.options.onClose();
    }
  }
  
  isConnected() {
    return this.eventSource && this.eventSource.readyState === EventSource.OPEN;
  }
}

export default SSEConnection;
