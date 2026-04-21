import './globals.css';

export const metadata = {
  title: 'IA Trader Pro',
  description: 'Dashboard para o IA Trader Pro bot.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className="bg-gray-900 text-gray-100">{children}</body>
    </html>
  );
}