import type { ReactNode } from 'react';

interface Props {
  sidebar: ReactNode;
  children: ReactNode;
}

export default function ChatLayout({ sidebar, children }: Props) {
  return (
    <div className="app-shell">
      <aside className="sidebar">{sidebar}</aside>
      <div className="chat-main">{children}</div>
    </div>
  );
}
