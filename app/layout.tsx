// app/layout.tsx

import '../app/globals.css';
import { ReactNode } from 'react';

export const metadata = {
  title: 'POS App',
  description: 'A simple POS system application',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body>
        <div className="container">{children}</div>
      </body>
    </html>
  );
}
