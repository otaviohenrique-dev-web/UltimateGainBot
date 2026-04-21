import './globals.css';

export const metadata = {
  title: 'Ultimate Gain',
  description: 'Dashboard para o Ultimate Gain bot.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-900 text-gray-100">{children}</body>
    </html>
  );
}