'use client';

import { useRef, useEffect, useState } from 'react';
import { Container, Form, InputGroup, Button } from 'react-bootstrap';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
};

export default function Home() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: input,
      };
      
      setMessages(prev => [...prev, userMessage]);
      setInput('');
      setIsLoading(true);

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: [...messages, userMessage].map(m => ({
              role: m.role,
              content: m.content,
            })),
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let assistantMessage = '';

        if (reader) {
          const assistantId = Date.now().toString();
          
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            assistantMessage += chunk;
            
            // Update the assistant message in real-time
            setMessages(prev => {
              const filtered = prev.filter(m => m.id !== assistantId);
              return [
                ...filtered,
                {
                  id: assistantId,
                  role: 'assistant' as const,
                  content: assistantMessage,
                },
              ];
            });
          }
        }
      } catch (error) {
        console.error('Chat error:', error);
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: 'Sorry, there was an error processing your request.',
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Container className="py-4">
      <h1 className="mb-4">Recipe Assistant Chat</h1>
      
      <Form onSubmit={handleSubmit}>
        <InputGroup className="mb-3">
          <Form.Control
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about recipes, ingredients, or cooking instructions..."
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </Button>
        </InputGroup>
      </Form>

      <div
        className="border rounded p-3 bg-dark"
        style={{ height: '400px', overflowY: 'auto' }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-2 p-2 rounded ${
              msg.role === 'user'
                ? 'bg-primary bg-opacity-25'
                : 'bg-secondary bg-opacity-50'
            }`}
            style={{ whiteSpace: 'pre-wrap' }}
          >
            <strong>{msg.role === 'user' ? 'You' : 'Assistant'}:</strong> {msg.content}
          </div>
        ))}
        {isLoading && messages[messages.length - 1]?.role === 'user' && (
          <div className="mb-2 p-2 rounded bg-secondary bg-opacity-25">
            <em>Thinking...</em>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </Container>
  );
}
