import { useState, useCallback } from 'react';

const OPENCLAW_URL = process.env.REACT_APP_OPENCLAW_URL || '/api/ai';

export function useOpenClaw() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const chat = useCallback(async (messages, options = {}) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${OPENCLAW_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages,
          model: options.model || 'moonshot/kimi-k2.6',
          temperature: options.temperature ?? 0.7,
          max_tokens: options.maxTokens ?? 2000,
        }),
      });

      if (!res.ok) {
        throw new Error(`AI request failed: ${res.status}`);
      }

      const data = await res.json();
      return data;
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  const generateHeadnotes = useCallback(async (caseId) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${OPENCLAW_URL}/generate-headnotes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: caseId }),
      });

      if (!res.ok) {
        throw new Error(`Headnote generation failed: ${res.status}`);
      }

      const data = await res.json();
      return data;
    } catch (e) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { chat, generateHeadnotes, loading, error };
}
