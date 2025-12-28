import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";

export const metadata = {
  title: "CryptoDash AI",
  description: "Market Data & Trading Bot Dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body>
        <div className="flex min-h-screen">
          {/* Fixed side menu */}
          <Sidebar />

          {/* Main scrolling area */}
          <main className="flex-1 ml-64 p-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}