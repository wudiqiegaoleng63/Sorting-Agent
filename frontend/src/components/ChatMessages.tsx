import { useEffect, useRef } from 'react';
import type { ChatMessage as ChatMessageType } from '../types/agent';
import ChatMessage from './ChatMessage';
import EmptyState from './EmptyState';

interface Props {
  messages: ChatMessageType[];
}

export default function ChatMessages({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="chat-messages">
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="chat-messages">
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
