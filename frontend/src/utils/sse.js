export function createSSEConnection(url, onMessage, onError) {
  const eventSource = new EventSource(url);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('SSE parse error:', e);
    }
  };

  eventSource.onerror = (error) => {
    console.error('SSE error:', error);
    if (onError) onError(error);
  };

  return () => {
    eventSource.close();
  };
}
