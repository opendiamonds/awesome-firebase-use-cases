import { useEffect, useRef, useState, useCallback } from 'react';
import { wsUrl } from '../config/api';

interface UseCollaborationProps {
  workspaceId: string;
  onReceiveXml: (xml: string) => void;
}

export const useCollaboration = ({ workspaceId, onReceiveXml }: UseCollaborationProps) => {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  
  // Use a ref for the callback so we don't reconnect when it changes
  const onReceiveRef = useRef(onReceiveXml);
  useEffect(() => {
    onReceiveRef.current = onReceiveXml;
  }, [onReceiveXml]);

  useEffect(() => {
    if (!workspaceId) return;

    const ws = new WebSocket(wsUrl(`/api/collab/ws/${workspaceId}`));
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      console.log(`Connected to workspace ${workspaceId}`);
    };

    ws.onmessage = (event) => {
      try {
        const data = event.data;
        // In this MVP, we just broadcast raw XML.
        // If data starts with <mxGraphModel or <mxfile, it's XML.
        if (typeof data === 'string' && (data.includes('<mxGraphModel') || data.includes('<mxfile'))) {
          onReceiveRef.current(data);
        }
      } catch (err) {
        console.error('Failed to parse websocket message', err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
      console.log('Disconnected from workspace');
      // Simple auto-reconnect could be implemented here
    };

    return () => {
      ws.close();
    };
  }, [workspaceId]);

  const broadcastXml = useCallback((xml: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(xml);
    }
  }, []);

  return {
    isConnected,
    broadcastXml
  };
};
